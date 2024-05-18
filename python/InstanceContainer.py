from PriorityQueue import PriorityQueue
from LLMShortTermMemory import LLMShortTermMemory
from websocket import create_connection
from Azure import Azure

# centralized instance container

# this class uses the singleton pattern to avoid multiple instantiations
class InstanceContainerClass:
  _instance = None

  def __new__(cls, *args, **kwargs):
    if cls._instance is None:
      cls._instance = super(InstanceContainerClass, cls).__new__(cls, *args, **kwargs)
      cls._instance.__initialize()
      return cls._instance

  def __initialize(self):
    # storage for the vtuber's queued up actions
    self.priority_queue = PriorityQueue()
    # azure tts/stt instance
    self.azure = Azure(self.priority_queue)
    # flask server
    self.app = None
    # SQLAlchemy db instance
    self.db = None
    # marshmallow instance
    self.ma = None
    # llm short term memory
    self.llm_short_term_memory = LLMShortTermMemory()
    # websocket connection instance
    self.ws = create_connection('ws://localhost:4000')
    # pytwitchapi instances
    self.twitch = None
    self.chat = None
    self.pubsub = None
    
    print('[CONFIG] Initialized InstanceContainer.')


InstanceContainer = InstanceContainerClass()
