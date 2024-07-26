from enums import PRIORITY_QUEUE_PRIORITY_MAP, PRIORITY_QUEUE_PRIORITIES
from Prompt import Prompt as PromptClass
import threading

# a priority queue of Prompt classes.
# this queue is thread-safe and blocking.
class PriorityQueue:
  def __init__(self):
    self.queue = {}
    for key in PRIORITY_QUEUE_PRIORITY_MAP.keys():
      self.queue[key] = []
    self.lock = threading.Lock()
    self.not_empty = threading.Condition(self.lock)

  def enqueue(
    self,
    prompt,
    priority,
    utterance_id = None,
    azure_speaking_style = None,
    username_to_ban = None,
    is_eleven_labs = False,
    should_generate_audio_file_only = False,
    pytwitchapi_args = {},
  ):
    with self.lock:
      Prompt = PromptClass(
        prompt=prompt,
        priority=priority,
        utterance_id=utterance_id,
        azure_speaking_style=azure_speaking_style,
        username_to_ban=username_to_ban,
        is_eleven_labs=is_eleven_labs,
        should_generate_audio_file_only=should_generate_audio_file_only,
        pytwitchapi_args=pytwitchapi_args
      )

      if priority in [
        PRIORITY_QUEUE_PRIORITIES['PRIORITY_BAN_USER'],
        PRIORITY_QUEUE_PRIORITIES['PRIORITY_GAME_INPUT'],
        PRIORITY_QUEUE_PRIORITIES['PRIORITY_IMAGE'],
        PRIORITY_QUEUE_PRIORITIES['PRIORITY_MIC_INPUT'],
        PRIORITY_QUEUE_PRIORITIES['PRIORITY_COLLAB_MIC_INPUT'],
      ]:
        # these priorities will overwrite the previous value on enqueue.
        if len(self.queue[priority]) == 0:
          self.queue[priority].append(Prompt)
        else:
          self.queue[priority][0] = Prompt
      elif priority == PRIORITY_QUEUE_PRIORITIES['PRIORITY_PUBSUB_EVENTS_QUEUE']:
        # this priority will build a long string containing all enqueued items.
        if len(self.queue[priority]) == 0:
          self.queue[priority].append(Prompt)
        else:
          # this is kind of hacky because it drops properties on the incoming Prompt. *shrug*
          self.queue[priority][0].prompt += f' {Prompt.prompt}'
      elif priority == PRIORITY_QUEUE_PRIORITIES['PRIORITY_TWITCH_CHAT_QUEUE']:
        # this priority will append the enqueued item, while keeping the list at length 3 or lower, removing the first item.
        if len(self.queue[priority]) < 3:
          self.queue[priority].append(Prompt)
        else:
          self.queue[priority][0] = self.queue[priority][1]
          self.queue[priority][1] = self.queue[priority][2]
          self.queue[priority][2] = Prompt
      elif priority == PRIORITY_QUEUE_PRIORITIES['PRIORITY_REMIND_ME']:
        # this priority will simply append the enqueued item.
        self.queue[priority].append(Prompt)
      
      self.not_empty.notify() # signal that the queue is not empty

  def dequeue(self):
    with self.lock:
      while True:
        for priority in PRIORITY_QUEUE_PRIORITY_MAP.keys():
          if len(self.queue[priority]):
            return self.queue[priority].pop(0)
        self.not_empty.wait() # signal that the queue is empty.
  
  def has_items(self):
    for priority in PRIORITY_QUEUE_PRIORITY_MAP.keys():
      if len(self.queue[priority]):
        return True
    return False

  def get_items(self):
    return self.queue
