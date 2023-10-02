import sys; sys.path.append('../pytwitchapi')
from flask import Flask, request
from log_error import log_error
from execute_action import execute_or_enqueue_action
from pytwitchapi import run_pytwitchapi, terminate_pytwitchapi
from threading import Thread, Event
import signal
import asyncio

shutdown_event = Event()

def sigint_handler(signum, frame):
  print("SIGINT (CTRL+C) detected!")
  shutdown_event.set()
  terminate_pytwitchapi()

signal.signal(signal.SIGINT, sigint_handler)

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

if __name__ == '__main__':
  threads = [
    Thread(target=lambda: app.run(debug=False, port=5001)),
    Thread(target=lambda: asyncio.run(run_pytwitchapi()))
  ]
  [t.start() for t in threads]
  [t.join() for t in threads]
