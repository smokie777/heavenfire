from __main__ import app # this file declares routes for the flask server in server.py
from flask import request
from log_error import log_error
from execute_action import execute_or_enqueue_action
from pytwitchapi import terminate_pytwitchapi
import signal
import os
import json
import config
from gen_image_captions import take_screenshot, gen_image_captions, gen_image_react_prompt
from time import sleep
from utils import move_emojis_to_end, conditionally_add_period
from gen_edited_luna_response import gen_edited_luna_response
from tts import gen_audio_file_and_subtitles, speak
from sing import sing
from enums import PRIORITY_QUEUE_PRIORITIES
from db import db_message_get_all

@app.route('/view_db', methods=['POST'])
async def _view_db():
  data = request.get_json()
  model = data['model']
  model = 'message'
  
  try:
    if model.lower() == 'message':
      print(db_message_get_all())

  except Exception as e:
    log_error(e, '/view_db')

  return {}

@app.route('/receive_prompt', methods=['POST'])
async def _receive_prompt():
  data = request.get_json()
  prompt = data['prompt']
  priority = data['priority']

  try:
    await execute_or_enqueue_action(prompt, priority)
  except Exception as e:
    log_error(e, '/receive_prompt')

  return {}

# speak_text bypasses most of the app flow, so it should be used sparingly
@app.route('/speak_text', methods=['POST'])
def _speak_text():
  data = request.get_json()
  text = data['text']

  try:
    config.is_busy = True
    edited = conditionally_add_period(move_emojis_to_end(gen_edited_luna_response(text)))
    # todo: should we send latency to websocket here?
    (output_filename, subtitles) = gen_audio_file_and_subtitles(edited)
    config.ws.send(json.dumps({ 'edited': edited, 'subtitles': subtitles }))
    speak(output_filename)
    config.is_busy = False
  except Exception as e:
    log_error(e, '/speak_text')

  return {}

@app.route('/react_to_screen', methods=['POST'])
async def _react_to_screen():
  data = request.get_json()

  try:
    take_screenshot()
    image_captions = gen_image_captions()
    print('Captions: ', image_captions)
    prompt = gen_image_react_prompt(image_captions, 'picture')
    await execute_or_enqueue_action(prompt, PRIORITY_QUEUE_PRIORITIES['PRIORITY_IMAGE'])
  except Exception as e:
    log_error(e, '/react_to_screen')

  return {}

@app.route('/erase_memory', methods=['POST'])
def _erase_memory():
  data = request.get_json()

  try:
    config.llm_short_term_memory.erase_memory()
    setattr(config, 'is_busy', False)
    print(f'is_busy -> {getattr(config, "is_busy")}')
  except Exception as e:
    log_error(e, '/erase_memory')

  return {}

@app.route('/cancel_speech', methods=['POST'])
def _cancel_speech():
  data = request.get_json()

  try:
    config.tts_green_light = False
    sleep(0.25);
    config.tts_green_light = True
  except Exception as e:
    log_error(e, '/cancel_speech')

  return {}

@app.route('/sing', methods=['POST'])
def _sing():
  data = request.get_json()
  song = data['song']

  try:
    config.is_busy = True
    sing(song)
    config.is_busy = False
  except Exception as e:
    log_error(e, '/sing')

  return {}

@app.route('/set_context', methods=['POST'])
def _set_context():
  data = request.get_json()
  context = data['context']

  try:
    config.llm_short_term_memory.set_context(context)
  except Exception as e:
    log_error(e, '/set_context')

  return {}

@app.route('/set_config_variable', methods=['POST'])
def _set_config_variable():
  data = request.get_json()
  name = data['name']
  value = data['value']

  try:
    setattr(config, name, value)
    print(f'{name} -> {getattr(config, name)}')
  except Exception as e:
    log_error(e, '/set_config_variable')

  return {}

@app.route('/shut_down_server', methods=['POST'])
def _shut_down_server():
  data = request.get_json()

  try:
    terminate_pytwitchapi()
    os.kill(os.getpid(), signal.SIGINT)
  except Exception as e:
    log_error(e, '/shut_down_server')

  return {}