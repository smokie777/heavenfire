from flask import Flask, request
from log_error import log_error
from execute_action import execute_or_enqueue_action
from pytwitchapi import run_pytwitchapi, terminate_pytwitchapi
from threading import Thread, Event
import signal
import asyncio
import os
import config
from gen_image_captions import take_screenshot, gen_image_captions, gen_image_react_prompt
from time import sleep

app = Flask(__name__)

@app.route('/receive_prompt', methods=['POST'])
def _receive_prompt():
  data = request.get_json()
  prompt = data['prompt']
  priority = data['priority']

  try:
    execute_or_enqueue_action(prompt, priority)
  except Exception as e:
    log_error(e, '/receive_prompt')

  return {}

@app.route('/react_to_screen', methods=['POST'])
def _react_to_screen():
  data = request.get_json()

  try:
    take_screenshot()
    image_captions = gen_image_captions()
    print('Captions: ', image_captions)
    prompt = gen_image_react_prompt(image_captions, 'picture')
    execute_or_enqueue_action(prompt, 'priority_image')
  except Exception as e:
    log_error(e, '/react_to_screen')

  return {}

@app.route('/erase_memory', methods=['POST'])
def _erase_memory():
  data = request.get_json()

  try:
    config.llm_short_term_memory.erase_memory()
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

@app.route('/shut_down_server', methods=['POST'])
def _shut_down_server():
  data = request.get_json()

  try:
    terminate_pytwitchapi()
    os.kill(os.getpid(), signal.SIGINT)
  except Exception as e:
    log_error(e, '/shut_down_server')

  return {}


if __name__ == '__main__':
  threads = [
    Thread(target=lambda: app.run(debug=False, port=5001)),
    Thread(target=lambda: asyncio.run(run_pytwitchapi()))
  ]
  [t.start() for t in threads]
  [t.join() for t in threads]
