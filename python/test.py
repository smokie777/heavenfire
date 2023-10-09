import unittest
from utils import move_emojis_to_end, remove_text_inside_parentheses
from PriorityQueue import PriorityQueue, priority_queue_map
from LLMShortTermMemory import LLMShortTermMemory

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
    m.add_user_message('(foo) bar (baz)')
    m.add_assistant_message('(foo)')
    m.clean_parentheses()
    self.assertEqual(m.messages[1]['content'], 'bar')
    self.assertEqual(m.messages[2]['content'], '(foo)')
    m.erase_memory()
    self.assertEqual(len(m.messages), 1)

class TestMoveEmojisToEnd(unittest.TestCase):
  def runTest(self):
    test_cases = [
      ('foo🖤bar', 'foobar 🖤'),
      ('Foo. 🖤. Bar.', 'Foo.. Bar. 🖤'), # this edge case seems a bit difficult to fix
      ('Foo 🖤, bar.', 'Foo, bar. 🖤'),
      ('🖤foo🖤bar🖤', 'foobar 🖤🖤🖤'),
      ('🖤', '🖤'),
      ('🖤🖤', '🖤🖤'),
      (' 🖤foo   ', 'foo 🖤')
    ]
    [self.assertEqual(
      move_emojis_to_end(i[0]),
      i[1]
    ) for i in test_cases]


if __name__ == '__main__':
  unittest.main()
