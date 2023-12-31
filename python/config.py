from PriorityQueue import PriorityQueue
from LLMShortTermMemory import LLMShortTermMemory
from websocket import create_connection

# the vtuber can't perform any actions while is_busy is True.
is_busy = False
# storage for the vtuber's queued up actions
priority_queue = PriorityQueue()
# llm short term memory
llm_short_term_memory = LLMShortTermMemory()
# llm fuzzy token limit
llm_fuzzy_token_limit = 750
# make this false for a couple seconds to terminate the audio playing loop.
tts_green_light = True
# seconds of delay bewteen ai responses
ai_response_delay = 2
# websocket connection instance
ws = create_connection('ws://localhost:4000')
# is the vtuber responding to twitch chat?
is_twitch_chat_react_on = True
# is the vtuber responding to twitch chat, but only if @ mentioned?
is_quiet_mode_on = True
# pytwitchapi instances
twitch = None
chat = None
pubsub = None
