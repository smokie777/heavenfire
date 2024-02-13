from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from PriorityQueue import PriorityQueue
from LLMShortTermMemory import LLMShortTermMemory
from websocket import create_connection

### INSTANCES
# azure tts/stt instance
azure = None
# initialize the flask server
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
# SQLAlchemy db instance
db = SQLAlchemy(app)
# marshmallow instance
ma = Marshmallow(app)
# storage for the vtuber's queued up actions
priority_queue = PriorityQueue()
# llm short term memory
llm_short_term_memory = LLMShortTermMemory()
# websocket connection instance
ws = create_connection('ws://localhost:4000')
# pytwitchapi instances
twitch = None
chat = None
pubsub = None

### FLAGS/TOGGLES
# the vtuber can't perform any actions while is_busy is True.
is_busy = False
# llm fuzzy token limit
llm_fuzzy_token_limit = 1000
# make this false for a couple seconds to terminate the audio playing loop.
tts_green_light = True
# seconds of delay bewteen ai responses
ai_response_delay = 2.5
# seconds of delay after mic input to prevent ai hearing itself on speakers
mic_input_delay = 1
# is the vtuber responding to twitch chat?
is_twitch_chat_react_on = True
# is the vtuber responding to twitch chat, but only if @ mentioned?
is_quiet_mode_on = True
# is singing in action
is_singing = False

### SERVER IN-MEMORY STORAGE
# stores tuples like ('remind foo to bar!', datetime)
remind_me_prompts_and_datetime_queue = []
