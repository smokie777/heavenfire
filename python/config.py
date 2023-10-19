from PriorityQueue import PriorityQueue
from LLMShortTermMemory import LLMShortTermMemory

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
ai_response_delay = 1
