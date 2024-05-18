import asyncio
from threading import Thread
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from InstanceContainer import InstanceContainer

InstanceContainer.app = Flask(__name__)
InstanceContainer.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
InstanceContainer.db = SQLAlchemy(InstanceContainer.app)
InstanceContainer.ma = Marshmallow(InstanceContainer.app)

import routes

from db import db_message_get_last_five

from pytwitchapi import run_pytwitchapi

from remind_me import remind_me_async_loop_run
from priority_queue import priority_queue_loop_run
from r_ctrl_stt import r_ctrl_stt_run

if __name__ == '__main__':
  # initialization
  with InstanceContainer.app.app_context():
    InstanceContainer.llm_short_term_memory.load_initial_messages(
      db_message_get_last_five()
    )
  print(InstanceContainer.llm_short_term_memory.messages[1:])

  # run apps together. intended usage
  threads = [
    Thread(target=lambda: InstanceContainer.app.run(debug=False, port=5001)),
    Thread(target=lambda: asyncio.run(run_pytwitchapi())),
    Thread(target=priority_queue_loop_run),
    Thread(target=remind_me_async_loop_run),
    Thread(target=r_ctrl_stt_run),
  ]

  [t.start() for t in threads]
  [t.join() for t in threads]
