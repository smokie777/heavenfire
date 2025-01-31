from flask import request
from log_error import log_error
from pytwitchapi import terminate_pytwitchapi
import signal
import os
import json
from InstanceContainer import InstanceContainer
from State import State
from gen_image_captions import take_screenshot, gen_image_captions, gen_image_react_prompt
from time import sleep
from utils import move_emojis_to_end, conditionally_add_period
from gen_edited_luna_response import gen_edited_luna_response
from sing import sing
from enums import PRIORITY_QUEUE_PRIORITIES
from db import db_message_get_by_page, db_event_get_by_page

@InstanceContainer.app.route('/receive_prompt', methods=['POST'])
def _receive_prompt():
  data = request.get_json()
  prompt = data['prompt']
  priority = data['priority']
  utterance_id = data['utterance_id'] if 'utterance_id' in data else None
  azure_speaking_style = data['azure_speaking_style'] if 'azure_speaking_style' in data else None

  try:
    InstanceContainer.priority_queue.enqueue(
      prompt=prompt,
      priority=priority,
      utterance_id=utterance_id,
      azure_speaking_style=azure_speaking_style
    )
  except Exception as e:
    log_error(e, '/receive_prompt')

  return {}

@InstanceContainer.app.route('/generate_audio_file', methods=['POST'])
def generate_audio_file():
  data = request.get_json()
  prompt = data['prompt']

  try:
    InstanceContainer.priority_queue.enqueue(
      prompt=prompt,
      priority=PRIORITY_QUEUE_PRIORITIES['PRIORITY_MIC_INPUT'],
      should_generate_audio_file_only=True
    )
  except Exception as e:
    log_error(e, '/receive_prompt')

  return {}

# speak_text bypasses most of the app flow, so it should be used sparingly
@InstanceContainer.app.route('/speak_text', methods=['POST'])
def _speak_text():
  data = request.get_json()
  text = data['text']

  try:
    State.is_busy = True
    edited = conditionally_add_period(move_emojis_to_end(gen_edited_luna_response(text)))
    # todo: should we send latency to websocket here?
    (output_filename, subtitles) = InstanceContainer.azure.gen_audio_file_and_subtitles(edited)
    InstanceContainer.ws.send(json.dumps({ 'edited': edited, 'subtitles': subtitles }))
    InstanceContainer.azure.speak(output_filename)
    State.is_busy = False
  except Exception as e:
    log_error(e, '/speak_text')

  return {}

@InstanceContainer.app.route('/react_to_screen', methods=['POST'])
def _react_to_screen():
  data = request.get_json()

  try:
    take_screenshot()
    image_captions = gen_image_captions()
    print('[ROUTES] Captions: ', image_captions)
    prompt = gen_image_react_prompt(image_captions, 'picture')
    InstanceContainer.priority_queue.enqueue(
      prompt=prompt,
      priority=PRIORITY_QUEUE_PRIORITIES['PRIORITY_IMAGE']
    )
  except Exception as e:
    log_error(e, '/react_to_screen')

  return {}

@InstanceContainer.app.route('/erase_memory', methods=['POST'])
def _erase_memory():
  data = request.get_json()

  try:
    InstanceContainer.llm_short_term_memory.erase_memory()
    State.is_busy = False
    print(f'[ROUTES] is_busy -> {State.is_busy}')
  except Exception as e:
    log_error(e, '/erase_memory')

  return {}

@InstanceContainer.app.route('/cancel_speech', methods=['POST'])
def _cancel_speech():
  data = request.get_json()

  try:
    State.tts_green_light = False
    sleep(0.25);
    State.tts_green_light = True
  except Exception as e:
    log_error(e, '/cancel_speech')

  return {}

@InstanceContainer.app.route('/sing', methods=['POST'])
def _sing():
  data = request.get_json()
  song = data['song']

  try:
    State.is_busy = True
    sing(song, InstanceContainer.azure)
    State.is_busy = False
  except Exception as e:
    log_error(e, '/sing')

  return {}

@InstanceContainer.app.route('/set_context', methods=['POST'])
def _set_context():
  data = request.get_json()
  context = data['context']

  try:
    InstanceContainer.llm_short_term_memory.set_context(context)
  except Exception as e:
    log_error(e, '/set_context')

  return {}

@InstanceContainer.app.route('/set_backend_state_variable', methods=['POST'])
def _set_backend_state_variable():
  data = request.get_json()
  name = data['name']
  value = data['value']

  try:
    if hasattr(State, name):
      setattr(State, name, value)
      print(f'[ROUTES] State.{name} -> {getattr(State, name)}')
    else:
      print(f'[ROUTES] No such property: State.{name}')
  except Exception as e:
    log_error(e, '/set_backend_state_variable')

  return {}

@InstanceContainer.app.route('/shut_down_server', methods=['POST'])
def _shut_down_server():
  data = request.get_json()

  try:
    terminate_pytwitchapi()
    os.kill(os.getpid(), signal.SIGINT)
  except Exception as e:
    log_error(e, '/shut_down_server')

  return {}

@InstanceContainer.app.route('/get_db_rows_by_page', methods=['POST'])
def _get_db_rows_by_page():
  data = request.get_json()
  model = data['model']
  page = data['page']
  rows = []
  
  try:
    if model.lower() == 'message':
      rows = db_message_get_by_page(page)
    elif model.lower() == 'event':
      rows = db_event_get_by_page(page)

  except Exception as e:
    log_error(e, '/get_db_rows_by_page')

  return {
    'rows': rows
  }

@InstanceContainer.app.route('/print_raffle_entries', methods=['POST'])
def _print_raffle_entries():
  data = request.get_json()

  return {
    'entries': list(State.raffle_entries_set)
  }

@InstanceContainer.app.route('/toggle_is_speaking_fast', methods=['POST'])
def _toggle_is_speaking_fast():
  data = request.get_json()
  State.is_speaking_fast = not State.is_speaking_fast

  return {}

@InstanceContainer.app.route('/process_luna_wheel_queue', methods=['POST'])
def _process_luna_wheel_queue():
  data = request.get_json()
  if len(State.luna_wheel_queue):
    del State.luna_wheel_queue[0]
  if len(State.luna_wheel_queue):
    InstanceContainer.ws.send(json.dumps({
      'luna_wheel': {
        'user_input': State.luna_wheel_queue[0]
      }
    }))

  return {}
