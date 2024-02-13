from enums import PRIORITY_QUEUE_PRIORITY_MAP

# a priority queue of Prompt classes.
class PriorityQueue:
  def __init__(self):
    self.queue = {}
    for key in PRIORITY_QUEUE_PRIORITY_MAP.keys():
      self.queue[key] = []

  def enqueue(self, Prompt):
    priority = Prompt.priority

    if priority in [
      'PRIORITY_BAN_USER',
      'PRIORITY_GAME_INPUT',
      'PRIORITY_IMAGE',
      'PRIORITY_MIC_INPUT',
      'PRIORITY_COLLAB_MIC_INPUT'
    ]:
      # these priorities will overwrite the previous value on enqueue.
      if len(self.queue[priority]) == 0:
        self.queue[priority].append(Prompt)
      else:
        self.queue[priority][0] = Prompt
    elif priority == 'PRIORITY_PUBSUB_EVENTS_QUEUE':
      # this priority will build a long string containing all enqueued items.
      if len(self.queue[priority]) == 0:
        self.queue[priority].append(Prompt)
      else:
        # this is kind of hacky because it drops properties on the incoming Prompt. *shrug*
        self.queue[priority][0].prompt += f' {Prompt.prompt}'
    elif priority == 'PRIORITY_TWITCH_CHAT_QUEUE':
      # this priority will append the enqueued item, while keeping the list at length 3 or lower, removing the first item.
      if len(self.queue[priority]) < 3:
        self.queue[priority].append(Prompt)
      else:
        self.queue[priority][0] = self.queue[priority][1]
        self.queue[priority][1] = self.queue[priority][2]
        self.queue[priority][2] = Prompt
    elif priority == 'PRIORITY_REMIND_ME':
      # this priority will simply append the enqueued item.
      self.queue[priority].append(Prompt)

  def dequeue(self):
    for priority in PRIORITY_QUEUE_PRIORITY_MAP.keys():
      if len(self.queue[priority]):
        return self.queue[priority].pop(0)
    return None
  
  def has_items(self):
    for priority in PRIORITY_QUEUE_PRIORITY_MAP.keys():
      if len(self.queue[priority]):
        return True
    return False

  def get_items(self):
    return self.queue
