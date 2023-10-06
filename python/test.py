import sys; sys.path.append('./llm')
import unittest
from server.PriorityQueue import PriorityQueue, priority_queue_map
from LLMShortTermMemory import LLMShortTermMemory, remove_text_inside_parentheses

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

class TestRemoveTextInsideParentheses(unittest.TestCase):
  def runTest(self):
    test_cases = [
      ('asdf', 'asdf'),
      ('(remove)', ''),
      ('(remove)asdf(remove)', 'asdf'),
      ('asdf(remove)asdf()', 'asdfasdf')
    ]
    [self.assertEqual(
      remove_text_inside_parentheses(i[0]),
      i[1]
    ) for i in test_cases]

class TestLLMShortTermMemory(unittest.TestCase):
  def runTest(self):
    m = LLMShortTermMemory()
    self.assertEqual(m.messages[0]['role'], 'system')
    m.add_user_message('foo1')
    m.add_assistant_message('foo2')
    m.add_user_message('foo3')
    m.add_assistant_message('foo4')
    m.clean_parentheses()
    m.trim()
    self.assertEqual(m.messages[-1]['role'], 'system')


if __name__ == '__main__':
  unittest.main()
