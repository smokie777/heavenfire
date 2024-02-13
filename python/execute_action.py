import config
from llm_openai import gen_llm_response
import json
from time import sleep, time
from enums import PRIORITY_QUEUE_PRIORITIES, TWITCH_EVENTS, AZURE_SPEAKING_STYLE_TAGS
from utils import extract_username_to_timeout_from_string
from pytwitchapi_helpers import ban_user_via_username
from db import db_message_insert_one
import asyncio
from concurrent.futures import ThreadPoolExecutor

def execute_or_enqueue_action(prompt, priority):
  config.priority_queue.enqueue(prompt, priority)
  if not config.is_busy:
    execute_action()

def execute_action():
  config.is_busy = True
  config.ws.send(json.dumps({ 'is_busy': True }))
  username_to_ban = ''

  (prompt, priority) = config.priority_queue.dequeue()

  if priority == PRIORITY_QUEUE_PRIORITIES['PRIORITY_BAN_USER']:
    username_to_ban = prompt.split('|')[0]
    prompt = prompt.split('|')[1]

  while prompt:
    speaking_style = ''

    for style, tag in AZURE_SPEAKING_STYLE_TAGS.items():
      if prompt.startswith(tag):
        prompt = prompt.replace(tag, '')
        speaking_style = style
    
    start_time = time()
    (prompt, raw, edited) = gen_llm_response(prompt)
    latency_llm = round((time() - start_time), 3)

    print('[LLM] Prompt: ', prompt)
    print('[LLM] Raw: ', raw)
    print('[LLM] Edited: ', edited)

    config.ws.send(json.dumps({
      'prompt': prompt, 'raw': raw, 'edited': edited, 'latency_llm': f'{latency_llm}s'
    }))

    start_time = time()
    (output_filename, subtitles) = config.azure.gen_audio_file_and_subtitles(edited, speaking_style)
    latency_tts = round((time() - start_time), 3)
    with config.app.app_context():
      db_message_insert_one(prompt=prompt, response=edited, latency_llm=latency_llm, latency_tts=latency_tts)

    print(f'[LLM] LLM: {latency_llm}s | TTS: {latency_tts}s')

    config.ws.send(json.dumps({
      'edited': edited, 'subtitles': subtitles, 'latency_tts': f'{latency_tts}s'
    }))

    if username_to_ban:
      config.ws.send(json.dumps({
        'twitch_event': {
          'event': TWITCH_EVENTS['BAN'],
          'username': username_to_ban,
          'value': None
        }
      }))

    config.azure.speak(output_filename)

    if '!timeout' in edited:
      username_to_timeout = extract_username_to_timeout_from_string(edited)
      if username_to_timeout:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        with ThreadPoolExecutor() as pool:
          # Ensure the loop runs in a new thread
          loop.run_in_executor(
            pool,
            asyncio.run,
            ban_user_via_username(username_to_timeout, 30, 'timed out by luna')
          )
    if (
      priority != PRIORITY_QUEUE_PRIORITIES['PRIORITY_MIC_INPUT']
      and priority != PRIORITY_QUEUE_PRIORITIES['PRIORITY_COLLAB_MIC_INPUT']
    ):
      sleep(config.ai_response_delay)

    (prompt, priority) = config.priority_queue.dequeue()

  config.ws.send(json.dumps({ 'is_busy': False }))
  config.is_busy = False
