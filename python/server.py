from flask import Flask
import asyncio
from remind_me import remind_me_start_async_loop
from pytwitchapi import run_pytwitchapi
from threading import Thread

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'

import routes

if __name__ == '__main__':
  app.run(debug=False, port=5001)

  # loop = asyncio.new_event_loop()

  # threads = [
  #   Thread(target=lambda: app.run(debug=False, port=5001)),
  #   # Thread(target=lambda: asyncio.run(run_pytwitchapi())),
  #   # Thread(target=remind_me_start_async_loop, args=(loop,))
  # ]

  # [t.start() for t in threads]
  # [t.join() for t in threads]
