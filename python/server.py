import asyncio
from threading import Thread

import config

import db # this import must happen after config

from Azure import Azure

import routes # this import must happen after db

from pytwitchapi import run_pytwitchapi # this import must happen after db

from remind_me import remind_me_async_loop_run
from priority_queue import priority_queue_loop_run
from r_ctrl_stt import r_ctrl_stt_run # this import must happen after Azure

if __name__ == '__main__':
  # initialization
  with config.app.app_context():
    config.llm_short_term_memory.load_initial_messages(db.db_message_get_last_five())

  print(config.llm_short_term_memory.messages[1:])
  config.azure = Azure()

  # run apps together. intended usage
  threads = [
    Thread(target=lambda: config.app.run(debug=False, port=5001)),
    Thread(target=lambda: asyncio.run(run_pytwitchapi())),
    Thread(target=priority_queue_loop_run),
    Thread(target=remind_me_async_loop_run),
    Thread(target=r_ctrl_stt_run),
  ]

  [t.start() for t in threads]
  [t.join() for t in threads]
