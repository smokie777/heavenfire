import config
from time import sleep
from gen_llm_response import gen_llm_response
from tts import gen_audio_file_and_subtitles, speak
from websocket import create_connection
import json
from constants import AZURE_SPEAKING_STYLE_TAGS
from time import sleep, time

ws = create_connection('ws://localhost:4000')

def execute_or_enqueue_action(prompt, priority):
  if config.is_busy:
    config.priority_queue.enqueue(prompt, priority)
  else:
    config.priority_queue.enqueue(prompt, priority)
    execute_action()

def execute_action():
  config.is_busy = True

  prompt = config.priority_queue.dequeue()
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

    ws.send(json.dumps({ 'prompt': prompt, 'raw': raw, 'edited': edited, 'latency_llm': latency_llm }))

    start_time = time()
    (output_filename, subtitles) = gen_audio_file_and_subtitles(edited, speaking_style)
    latency_tts = f'{round((time() - start_time), 3)}s'

    print(f'LLM: {latency_llm} | TTS: {latency_tts}')

    ws.send(json.dumps({ 'edited': edited, 'subtitles': subtitles, 'latency_tts': latency_tts }))

    speak(output_filename)

    prompt = config.priority_queue.dequeue()

  sleep(config.ai_response_delay)

  ws.send(json.dumps({ 'is_busy': False }))
  config.is_busy = False
