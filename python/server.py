from flask import Flask
import asyncio
from remind_me import remind_me_start_async_loop
from pytwitchapi import run_pytwitchapi
from threading import Thread
import config

import db # this import must happen after config
import routes # this import must happen after db

if __name__ == '__main__':
  # run apps individually. should be done for testing purposes only
  config.app.run(debug=False, port=5001)
  # asyncio.run(run_pytwitchapi())
  # remind_me_start_async_loop(loop,)

  # run apps together. intended usage
  # loop = asyncio.new_event_loop()

  # threads = [
  #   Thread(target=lambda: app.run(debug=False, port=5001)),
  #   Thread(target=lambda: asyncio.run(run_pytwitchapi())),
  #   Thread(target=remind_me_start_async_loop, args=(loop,))
  # ]

  # [t.start() for t in threads]
  # [t.join() for t in threads]
