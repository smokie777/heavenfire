from flask import Flask
import asyncio
from threading import Thread

import config

import db # this import must happen after config
import routes # this import must happen after db
from pytwitchapi import run_pytwitchapi # this import must happen after db

from remind_me import remind_me_start_async_loop

if __name__ == '__main__':
  # initialization
  with config.app.app_context():
    config.llm_short_term_memory.load_initial_messages(db.db_message_get_last_three())

  # run apps individually. should be done for testing purposes only
  # config.app.run(debug=False, port=5001)
  # asyncio.run(run_pytwitchapi())
  # remind_me_start_async_loop(loop,)

  # run apps together. intended usage
  loop = asyncio.new_event_loop()

  threads = [
    Thread(target=lambda: config.app.run(debug=False, port=5001)),
    Thread(target=lambda: asyncio.run(run_pytwitchapi())),
    Thread(target=remind_me_start_async_loop, args=(loop,))
  ]

  [t.start() for t in threads]
  [t.join() for t in threads]
