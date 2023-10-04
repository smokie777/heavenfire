import unittest
from server.PriorityQueue import PriorityQueue, priority_queue_map

class TestPriorityQueue(unittest.TestCase):
  def runTest(self):
    q = PriorityQueue()

    for key in priority_queue_map.keys():
      q.enqueue(('foo' + str(key), key))
      item = q.get_items()[key]
      self.assertEqual(
        item if type(item) is str else item[-1],
        'foo' + str(key),
        'priority queue cant enqueue'
      )

    for key in priority_queue_map.keys():
      item = q.dequeue()
      self.assertEqual(
        item,
        'foo' + str(key),
        'priority queue cant dequeue'
      )


if __name__ == '__main__':
  unittest.main()
