import unittest
from utils import move_emojis_to_end, remove_text_inside_parentheses
from PriorityQueue import PriorityQueue, PRIORITY_QUEUE_MAP
from LLMShortTermMemory import LLMShortTermMemory, memory_trim_index
from gen_image_captions import gen_image_react_prompt
from prompts import system

class TestPriorityQueue(unittest.TestCase):
  def runTest(self):
    q = PriorityQueue()

    self.assertFalse(q.has_items(), 'priority queue has_items isnt working - false positive 1')

    for key in PRIORITY_QUEUE_MAP.keys():
      q.enqueue('foo' + str(key), key)
      self.assertTrue(q.has_items(), 'priority queue has_items isnt working - false negative')
      item = q.get_items()[key]
      self.assertEqual(
        item if type(item) is str else item[-1],
        'foo' + str(key),
        'priority queue cant enqueue'
      )

    for key in PRIORITY_QUEUE_MAP.keys():
      (item, priority) = q.dequeue()
      self.assertEqual(
        item,
        'foo' + str(key),
        'priority queue cant dequeue (incorrect returned item)'
      )
      self.assertEqual(
        priority,
        str(key),
        'priority queue cant dequeue (incorrect returned priority)'
      )
    
    self.assertFalse(q.has_items(), 'priority queue has_items isnt working - false positive 2')

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
    self.assertEqual(m.messages[0]['role'], 'system')
    self.assertEqual(len(m.messages), memory_trim_index)
    m.add_user_message('(foo) bar (baz)')
    m.add_assistant_message('(foo)')
    m.clean_parentheses()
    self.assertEqual(m.messages[memory_trim_index + 0]['content'], 'bar')
    self.assertEqual(m.messages[memory_trim_index + 1]['content'], '(foo)')
    m.erase_memory()
    self.assertEqual(len(m.messages), memory_trim_index)
    m.set_context('Today, we are playing Path of Exile.')
    self.assertEqual(m.messages[0]['content'], f'{system} Today, we are playing Path of Exile.')

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

class TestImageReacts(unittest.TestCase):
  def runTest(self):
    azure_captions = [{'text': 'a computer screen shot of a cartoon animal', 'confidence': 0.7418550252914429, 'boundingBox': {'x': 0, 'y': 0, 'w': 2560, 'h': 1440}}, {'text': 'a cartoon of a cat woman', 'confidence': 0.6461490392684937, 'boundingBox': {'x': 262, 'y': 50, 'w': 1829, 'h': 1318}}, {'text': 'a screenshot of a computer game', 'confidence': 0.7590510249137878, 'boundingBox': {'x': 333, 'y': 382, 'w': 1036, 'h': 1012}}, {'text': 'a close-up of a blue string', 'confidence': 0.6619687676429749, 'boundingBox': {'x': 1049, 'y': 800, 'w': 128, 'h': 179}}, {'text': 'a close up of an eye', 'confidence': 0.8309906721115112, 'boundingBox': {'x': 1303, 'y': 366, 'w': 103, 'h': 108}}, {'text': 'a cartoon of a cat with yellow eyes', 'confidence': 0.6563021540641785, 'boundingBox': {'x': 1088, 'y': 125, 'w': 536, 'h': 560}}]
    prompt = "You've just seen a picture with the following image recognition tags. Give it your best react! Tags: a cartoon of a cat woman, a close-up of a blue string, a close up of an eye, a cartoon of a cat with yellow eyes"
    self.assertEqual(
      gen_image_react_prompt(azure_captions, 'picture')
        .replace('(ask a question somewhere in the response.) ', ''),
      prompt
    )


if __name__ == '__main__':
  unittest.main()
