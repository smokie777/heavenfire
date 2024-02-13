import unittest
from utils import move_emojis_to_end, remove_text_inside_parentheses, extract_username_to_timeout_from_string
from PriorityQueue import PriorityQueue
from LLMShortTermMemory import LLMShortTermMemory, memory_trim_index
from gen_image_captions import gen_image_react_prompt
from prompts import system
from helpers import obfuscate_prompt_username
from datetime import datetime
from Prompt import Prompt

class TestPriorityQueue(unittest.TestCase):
  def runTest(self):
    q = PriorityQueue()

    self.assertFalse(q.has_items(), 'priority queue has_items: empty queue should not have items')

    for priority in [
      'PRIORITY_BAN_USER',
      'PRIORITY_GAME_INPUT',
      'PRIORITY_IMAGE',
      'PRIORITY_MIC_INPUT',
      'PRIORITY_COLLAB_MIC_INPUT'
    ]:
      q.enqueue(Prompt(prompt='foo', priority=priority))
      q.enqueue(Prompt(prompt='foo1', priority=priority))
      self.assertEqual(
        q.get_items()[priority][0].prompt,
        'foo1',
        f'cant enqueue {priority}'
      )

    q.enqueue(Prompt(prompt='foo', priority='PRIORITY_PUBSUB_EVENTS_QUEUE'))
    q.enqueue(Prompt(prompt='foo1', priority='PRIORITY_PUBSUB_EVENTS_QUEUE'))
    self.assertEqual(
      q.get_items()['PRIORITY_PUBSUB_EVENTS_QUEUE'][0].prompt,
      'foo foo1',
      'cant enqueue PRIORITY_PUBSUB_EVENTS_QUEUE'
    )

    q.enqueue(Prompt(prompt='foo', priority='PRIORITY_REMIND_ME'))
    q.enqueue(Prompt(prompt='foo1', priority='PRIORITY_REMIND_ME'))

    self.assertEqual(
      q.get_items()['PRIORITY_REMIND_ME'][0].prompt,
      'foo',
      'cant enqueue PRIORITY_REMIND_ME'
    )
    self.assertEqual(
      q.get_items()['PRIORITY_REMIND_ME'][1].prompt,
      'foo1',
      'cant enqueue PRIORITY_REMIND_ME'
    )

    q.enqueue(Prompt(prompt='foo', priority='PRIORITY_TWITCH_CHAT_QUEUE'))
    q.enqueue(Prompt(prompt='foo1', priority='PRIORITY_TWITCH_CHAT_QUEUE'))
    q.enqueue(Prompt(prompt='foo2', priority='PRIORITY_TWITCH_CHAT_QUEUE'))
    self.assertEqual(
      len(q.get_items()['PRIORITY_TWITCH_CHAT_QUEUE']),
      3,
      'cant enqueue PRIORITY_TWITCH_CHAT_QUEUE'
    )
    q.enqueue(Prompt(prompt='foo3', priority='PRIORITY_TWITCH_CHAT_QUEUE'))
    self.assertEqual(
      len(q.get_items()['PRIORITY_TWITCH_CHAT_QUEUE']),
      3,
      'cant enqueue PRIORITY_TWITCH_CHAT_QUEUE'
    )
    self.assertEqual(
      q.get_items()['PRIORITY_TWITCH_CHAT_QUEUE'][0].prompt,
      'foo1',
      'cant enqueue PRIORITY_TWITCH_CHAT_QUEUE'
    )

    self.assertTrue(q.has_items(), 'priority queue has_items: non-empty queue should have items')

    # test dequeue by dequeueing all previously enqueued items
    Item = q.dequeue()
    self.assertEqual(
      Item.prompt,
      'foo1',
      f'priority queue cant dequeue PRIORITY_BAN_USER (incorrect returned item)'
    )
    self.assertEqual(
      Item.priority,
      'PRIORITY_BAN_USER',
      f'priority queue cant dequeue PRIORITY_BAN_USER (incorrect returned priority)'
    )

    Item = q.dequeue()
    self.assertEqual(
      Item.prompt,
      'foo1',
      f'priority queue cant dequeue PRIORITY_GAME_INPUT (incorrect returned item)'
    )
    self.assertEqual(
      Item.priority,
      'PRIORITY_GAME_INPUT',
      f'priority queue cant dequeue PRIORITY_GAME_INPUT (incorrect returned priority)'
    )

    Item = q.dequeue()
    self.assertEqual(
      Item.prompt,
      'foo1',
      f'priority queue cant dequeue PRIORITY_IMAGE (incorrect returned item)'
    )
    self.assertEqual(
      Item.priority,
      'PRIORITY_IMAGE',
      f'priority queue cant dequeue PRIORITY_IMAGE (incorrect returned priority)'
    )

    Item = q.dequeue()
    self.assertEqual(
      Item.prompt,
      'foo foo1',
      f'priority queue cant dequeue PRIORITY_PUBSUB_EVENTS_QUEUE (incorrect returned item)'
    )
    self.assertEqual(
      Item.priority,
      'PRIORITY_PUBSUB_EVENTS_QUEUE',
      f'priority queue cant dequeue PRIORITY_PUBSUB_EVENTS_QUEUE (incorrect returned priority)'
    )

    Item = q.dequeue()
    self.assertEqual(
      Item.prompt,
      'foo1',
      f'priority queue cant dequeue PRIORITY_MIC_INPUT (incorrect returned item)'
    )
    self.assertEqual(
      Item.priority,
      'PRIORITY_MIC_INPUT',
      f'priority queue cant dequeue PRIORITY_MIC_INPUT (incorrect returned priority)'
    )

    Item = q.dequeue()
    self.assertEqual(
      Item.prompt,
      'foo1',
      f'priority queue cant dequeue PRIORITY_COLLAB_MIC_INPUT (incorrect returned item)'
    )
    self.assertEqual(
      Item.priority,
      'PRIORITY_COLLAB_MIC_INPUT',
      f'priority queue cant dequeue PRIORITY_COLLAB_MIC_INPUT (incorrect returned priority)'
    )

    for _item in ['foo', 'foo1']:
      Item = q.dequeue()
      self.assertEqual(
        Item.prompt,
        _item,
        f'priority queue cant dequeue PRIORITY_REMIND_ME (incorrect returned item)'
      )
      self.assertEqual(
        Item.priority,
        'PRIORITY_REMIND_ME',
        f'priority queue cant dequeue PRIORITY_REMIND_ME (incorrect returned priority)'
      )

    for prompt in ['foo1', 'foo2', 'foo3']:
      Item = q.dequeue()
      self.assertEqual(
        Item.prompt,
        prompt,
        f'priority queue cant dequeue PRIORITY_TWITCH_CHAT_QUEUE (incorrect returned item)'
      )
      self.assertEqual(
        Item.priority,
        'PRIORITY_TWITCH_CHAT_QUEUE',
        f'priority queue cant dequeue PRIORITY_TWITCH_CHAT_QUEUE (incorrect returned priority)'
      )
        
    self.assertFalse(q.has_items(), 'priority queue has_items: empty queue should not have items')

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
    self.assertEqual(m.messages[0]['content'], f'{system} [Context description] Today, we are playing Path of Exile.')
    m = LLMShortTermMemory()
    m.load_initial_messages([
      {
        'created_at': datetime.now(),
        'prompt': 'foo',
        'response': 'bar',
        'latency_llm': 0.123,
        'latency_tts': 0.456,
      },
      {
        'created_at': datetime.now(),
        'prompt': 'foo1',
        'response': 'bar1',
        'latency_llm': 0.123,
        'latency_tts': 0.456,
      },
    ])
    self.assertEqual(m.messages[-1]['content'], 'bar1.')
    self.assertEqual(m.messages[-2]['content'], 'foo1')
    m = LLMShortTermMemory()
    with self.assertRaises(RuntimeError):
      m.load_initial_messages([
        {
          'created_at': datetime.now(),
          'prompt': 'foo',
          'response': 'bar',
          'latency_llm': 0.123,
          'latency_tts': 0.456,
        },
      ] * 4)

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

class TestExtractUsernameToTimeoutFromString(unittest.TestCase):
  def runTest(self):
    test_cases = [
      '!timeout spam_username_333',
      '!timeout spam_username_333.',
      '!timeout spam_username_333!!!'
    ]
    [self.assertEqual(
      extract_username_to_timeout_from_string(test_case),
      'spam_username_333'
    ) for test_case in test_cases]

class TestObfuscatePromptUsername:
  def runTest(self):
    test_cases = [
      ('user_name: text here', 'username: text here'),
      ('another_text without username', 'another_text without username'),
      ('second_user: some other text', 'username: some other text'),
      ('text with no user name prefix', 'text with no user name prefix'),
      ('third_user_name: another piece of text', 'username: another piece of text'),
      ('no user_name: another piece of text', 'no username: another piece of text'),
      ('smokie_777: text', 'smokie_777: text'),
    ]
    [self.assertEqual(
      obfuscate_prompt_username(i[0]),
      i[1]
    ) for i in test_cases]


if __name__ == '__main__':
  unittest.main()
