PRIORITY_QUEUE_MAP = {
  # highest priority
  'priority_game_input': 1,
  'priority_image': 2,
  'priority_pubsub_events_queue': 3,
  'priority_mic_input': 4,
  'priority_collab_mic_input': 5,
  'priority_twitch_chat_queue': 6,
  # lowest priority
}

class PriorityQueue:
  def __init__(self):
    self.queue = {
      'priority_game_input': '',
      'priority_image': '',
      'priority_pubsub_events_queue': [],
      'priority_mic_input': '',
      'priority_collab_mic_input': '',
      'priority_twitch_chat_queue': []
    }

  def enqueue(self, item, priority):
    if type(self.queue[priority]) is str:
      self.queue[priority] = item
    elif type(self.queue[priority]) is list:
      self.queue[priority].append(item)

  def dequeue(self):
    # returns tuple (item, priority)
    for key in PRIORITY_QUEUE_MAP.keys():
      if type(self.queue[key]) is str and self.queue[key] != '':
        ret = self.queue[key]
        self.queue[key] = ''
        return (ret, key);
      elif type(self.queue[key]) is list and len(self.queue[key]) != 0:
        if key == 'priority_twitch_chat_queue' and len(self.queue[key]) > 3:
          self.queue[key] = self.queue[key][len(self.queue[key])-3:]
          return (self.queue[key].pop(0), key)
        elif key == 'priority_pubsub_events_queue' and len(self.queue[key]) != 0:
          # combine all events in queue into one prompt, in case many bits/subs come in at once.
          ret = ' '.join(self.queue[key])
          self.queue[key] = []
          return (ret, key)
    return (None, None)
  
  def has_items(self):
    for key in PRIORITY_QUEUE_MAP.keys():
      if not (self.queue[key] == '' or self.queue[key] == []):
        return True
    return False

  def get_items(self):
    return self.queue


if __name__ == '__main__':
  priority_queue = PriorityQueue()
  priority_queue.enqueue('blah', 'priority_game_input')
  (prompt, priority) = priority_queue.dequeue()
  print(prompt)
  print(priority)
  