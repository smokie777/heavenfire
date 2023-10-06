import sys; sys.path.append('../llm')
from PriorityQueue import PriorityQueue
from LLMShortTermMemory import LLMShortTermMemory

# the vtuber can't perform any actions while is_busy is True.
is_busy = False
# storage for the vtuber's queued up actions
priority_queue = PriorityQueue()
# llm short term memory
llm_short_term_memory = LLMShortTermMemory()
