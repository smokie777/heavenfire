priority_queue_map = {
  1: 'pubsub_events_queue',
  2: 'mic_input',
  3: 'collab_mic_input',
  4: 'image',
  5: 'twitch_chat_queue'
}

class PriorityQueue:
  def __init__(self):
    self.queue = {
      'pubsub_events_queue': [],
      'mic_input': '',
      'collab_mic_input': '',
      'image': '',
      'twitch_chat_queue': []
    }

  def enqueue(self, prompt, priority):
    key = priority_queue_map[priority]
    if type(self.queue[key]) is str:
      self.queue[key] = prompt
    elif type(self.queue[key]) is list:
      self.queue[key].append(prompt)

  def dequeue(self):
    for key in priority_queue_map.values():
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
  q = PriorityQueue()
  q.enqueue('foo', 1)
  print(q.get_items())
