PRIORITY_QUEUE_MAP = {
  'priority_pubsub_events_queue': 1,
  'priority_mic_input': 2,
  'priority_collab_mic_input': 3,
  'priority_image': 4,
  'priority_twitch_chat_queue': 5,
}

class PriorityQueue:
  def __init__(self):
    self.queue = {
      'priority_pubsub_events_queue': [],
      'priority_mic_input': '',
      'priority_collab_mic_input': '',
      'priority_image': '',
      'priority_twitch_chat_queue': []
    }

  def enqueue(self, promptAndPriority):
    prompt, priority = promptAndPriority
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
        return self.queue[key].pop(0)
    return ''

  def get_items(self):
    return self.queue


if __name__ == '__main__':
  True
