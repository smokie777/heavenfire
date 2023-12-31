from enums import PRIORITY_QUEUE_PRIORITY_MAP

class PriorityQueue:
  def __init__(self):
    self.queue = {}
    for key in PRIORITY_QUEUE_PRIORITY_MAP.keys():
      self.queue[key] = []

  def enqueue(self, item, priority):
    if priority in [
      'PRIORITY_BAN_USER',
      'PRIORITY_GAME_INPUT',
      'PRIORITY_IMAGE',
      'PRIORITY_MIC_INPUT',
      'PRIORITY_COLLAB_MIC_INPUT'
    ]:
      # these priorities will overwrite the previous value on enqueue.
      if len(self.queue[priority]) == 0:
        self.queue[priority].append(item)
      else:
        self.queue[priority][0] = item
    elif priority == 'PRIORITY_PUBSUB_EVENTS_QUEUE':
      # this priority will build a long string containing all enqueued items.
      if len(self.queue[priority]) == 0:
        self.queue[priority].append(item)
      else:
        self.queue[priority][0] += f' {item}'
    elif priority == 'PRIORITY_TWITCH_CHAT_QUEUE':
      # this priority will append the enqueued item, while keeping the list at length 3 or lower, removing the first item.
      if len(self.queue[priority]) < 3:
        self.queue[priority].append(item)
      else:
        self.queue[priority][0] = self.queue[priority][1]
        self.queue[priority][1] = self.queue[priority][2]
        self.queue[priority][2] = item

  def dequeue(self):
    # returns tuple (item, priority)
    for priority in PRIORITY_QUEUE_PRIORITY_MAP.keys():
      if len(self.queue[priority]):
        return (self.queue[priority].pop(0), priority)
    return (None, None)
  
  def has_items(self):
    for priority in PRIORITY_QUEUE_PRIORITY_MAP.keys():
      if len(self.queue[priority]):
        return True
    return False

  def get_items(self):
    return self.queue
