import config
from llm_openai import gen_llm_response
import json
from time import sleep, time
from enums import PRIORITY_QUEUE_PRIORITIES, TWITCH_EVENTS
from utils import extract_username_to_timeout_from_string
from pytwitchapi_helpers import ban_user_via_username
from db import db_message_insert_one
import asyncio
from concurrent.futures import ThreadPoolExecutor
from Prompt import Prompt

def execute_or_enqueue_action(
  prompt,
  priority,
  utterance_id = None,
  azure_speaking_style = None,
  username_to_ban = None
):
  config.priority_queue.enqueue(
    Prompt(
      prompt=prompt,
      priority=priority,
      utterance_id=utterance_id,
      azure_speaking_style=azure_speaking_style,
      username_to_ban=username_to_ban
    )
  )
  if not config.is_busy:
    execute_action()

def execute_action():
  config.is_busy = True
  config.ws.send(json.dumps({ 'is_busy': True }))

  Prompt = config.priority_queue.dequeue()

  while Prompt:
    start_time = time()
    (prompt, raw, edited) = gen_llm_response(Prompt.prompt)
    latency_llm = round((time() - start_time), 3)

    print('[LLM] Prompt: ', prompt)
    print('[LLM] Raw: ', raw)
    print('[LLM] Edited: ', edited)

    config.ws.send(json.dumps({
      'prompt': prompt, 'raw': raw, 'edited': edited, 'latency_llm': f'{latency_llm}s'
    }))

    start_time = time()
    (output_filename, subtitles) = config.azure.gen_audio_file_and_subtitles(
      edited,
      Prompt.azure_speaking_style
    )
    latency_tts = round((time() - start_time), 3)
    with config.app.app_context():
      db_message_insert_one(prompt=prompt, response=edited, latency_llm=latency_llm, latency_tts=latency_tts)

    print(f'[LLM] LLM: {latency_llm}s | TTS: {latency_tts}s')

    config.ws.send(json.dumps({
      'edited': edited, 'subtitles': subtitles, 'latency_tts': f'{latency_tts}s'
    }))

    if Prompt.username_to_ban:
      loop = asyncio.new_event_loop()
      asyncio.set_event_loop(loop)
      with ThreadPoolExecutor() as pool:
        # Ensure the loop runs in a new thread
        loop.run_in_executor(
          pool,
          asyncio.run,
          ban_user_via_username(Prompt.username_to_ban, None, 'banned via !ban')
        )
      config.ws.send(json.dumps({
        'twitch_event': {
          'event': TWITCH_EVENTS['BAN'],
          'username': Prompt.username_to_ban,
          'value': None
        }
      }))

    config.azure.speak(output_filename)

    if Prompt.utterance_id:
      config.ws.send(json.dumps({ 'utterance_id': Prompt.utterance_id }))

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
      Prompt.priority != PRIORITY_QUEUE_PRIORITIES['PRIORITY_MIC_INPUT']
      and Prompt.priority != PRIORITY_QUEUE_PRIORITIES['PRIORITY_COLLAB_MIC_INPUT']
    ):
      sleep(config.ai_response_delay)

    Prompt = config.priority_queue.dequeue()

  config.ws.send(json.dumps({ 'is_busy': False }))
  config.is_busy = False
