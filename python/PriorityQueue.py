PRIORITY_QUEUE_MAP = {
  'priority_game_input': 1,
  'priority_pubsub_events_queue': 2,
  'priority_mic_input': 3,
  'priority_collab_mic_input': 4,
  'priority_image': 5,
  'priority_twitch_chat_queue': 6,
}

class PriorityQueue:
  def __init__(self):
    self.queue = {
      'priority_game_input': '',
      'priority_pubsub_events_queue': [],
      'priority_mic_input': '',
      'priority_collab_mic_input': '',
      'priority_image': '',
      'priority_twitch_chat_queue': []
    }

  def enqueue(self, prompt, priority):
    if type(self.queue[priority]) is str:
      self.queue[priority] = prompt
    elif type(self.queue[priority]) is list:
      self.queue[priority].append(prompt)

  def dequeue(self):
    for key in PRIORITY_QUEUE_MAP.keys():
      if type(self.queue[key]) is str and self.queue[key] != '':
        ret = self.queue[key]
        self.queue[key] = ''
        return ret;
      elif type(self.queue[key]) is list and len(self.queue[key]) != 0:
        if key == 'priority_twitch_chat_queue' and len(self.queue[key]) > 3:
          self.queue[key] = self.queue[key][len(self.queue[key])-3:]
        return self.queue[key].pop(0)
    return ''
  
  def has_items(self):
    for key in PRIORITY_QUEUE_MAP.keys():
      if not (self.queue[key] == '' or self.queue[key] == []):
        return True
    return False

  def get_items(self):
    return self.queue


if __name__ == '__main__':
  True
