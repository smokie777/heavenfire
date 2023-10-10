from flask import Flask, request
from log_error import log_error
from execute_action import execute_or_enqueue_action
from pytwitchapi import run_pytwitchapi, terminate_pytwitchapi
from threading import Thread, Event
import signal
import asyncio
import os

app = Flask(__name__)

@app.route('/receive_prompt', methods=['POST'])
def _receive_prompt():
  data = request.get_json()
  prompt = data['prompt']
  priority = data['priority']

  try:
    execute_or_enqueue_action((prompt, priority))
  except Exception as e:
    log_error(e, '/receive_prompt')

  return {}

@app.route('/the_testing_endpoint', methods=['POST'])
def _the_testing_endpoint():
  data = request.get_json()

  try:
    terminate_pytwitchapi()
    os.kill(os.getpid(), signal.SIGINT)
  except Exception as e:
    log_error(e, '/the_testing_endpoint')

  return {}


if __name__ == '__main__':
  threads = [
    Thread(target=lambda: app.run(debug=False, port=5001)),
    Thread(target=lambda: asyncio.run(run_pytwitchapi()))
  ]
  [t.start() for t in threads]
  [t.join() for t in threads]
