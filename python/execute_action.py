import config
from time import sleep
from llm_openai import gen_llm_response
from tts import gen_audio_file_and_subtitles, speak
import json
from enums import AZURE_SPEAKING_STYLE_TAGS
from time import sleep, time
from enums import PRIORITY_QUEUE_PRIORITIES, TWITCH_EVENTS
from utils import extract_username_to_timeout_from_string
from pytwitchapi_helpers import ban_user_via_username

async def execute_or_enqueue_action(prompt, priority):
  config.priority_queue.enqueue(prompt, priority)
  if not config.is_busy:
    await execute_action()

async def execute_action():
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
    latency_llm = f'{round((time() - start_time), 3)}s'

    print('Prompt: ', prompt)
    print('Raw: ', raw)
    print('Edited: ', edited)

    config.ws.send(json.dumps({ 'prompt': prompt, 'raw': raw, 'edited': edited, 'latency_llm': latency_llm }))

    start_time = time()
    (output_filename, subtitles) = gen_audio_file_and_subtitles(edited, speaking_style)
    latency_tts = f'{round((time() - start_time), 3)}s'

    print(f'LLM: {latency_llm} | TTS: {latency_tts}')

    config.ws.send(json.dumps({ 'edited': edited, 'subtitles': subtitles, 'latency_tts': latency_tts }))

    if username_to_ban:
      config.ws.send(json.dumps({
        'twitch_event': {
          'event': TWITCH_EVENTS['BAN'],
          'username': username_to_ban,
          'value': None
        }
      }))

    speak(output_filename)

    if '!timeout' in edited:
      username_to_timeout = extract_username_to_timeout_from_string(edited)
      if username_to_timeout:
        await ban_user_via_username(username_to_timeout, 60, 'timed out by luna')

    if (
      priority != PRIORITY_QUEUE_PRIORITIES['PRIORITY_MIC_INPUT']
      and priority != PRIORITY_QUEUE_PRIORITIES['PRIORITY_COLLAB_MIC_INPUT']
    ):
      sleep(config.ai_response_delay)

    (prompt, priority) = config.priority_queue.dequeue()

  config.ws.send(json.dumps({ 'is_busy': False }))
  config.is_busy = False
