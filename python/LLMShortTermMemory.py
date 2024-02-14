from prompts import system
from utils import remove_text_inside_parentheses, move_emojis_to_end, conditionally_add_period
from gen_edited_luna_response import gen_edited_luna_response

# if the "default" messages is ever more than the system message, need to edit this variable accordingly
memory_trim_index = 1

class LLMShortTermMemory:
  def __init__(self):
    self.messages = [{ 'role': 'system', 'content': system }]

  def set_context(self, context):
    self.messages[0]['content'] = f'{system} [Context description] {context}' if context else system

  def add_user_message(self, content):
    self.messages.append({ 'role': 'user', 'content': content })

  def add_assistant_message(self, content):
    raw = content
    try:
      edited = conditionally_add_period(move_emojis_to_end(gen_edited_luna_response(content)))
      self.messages.append({
        'role': 'assistant',
        'content': edited
      })
      return (raw, edited)
    except:
      # there is an annoying IndexError here that I just can't quite figure out Madge
      self.messages.pop() # remove the last user message
      error_speech = 'I just threw an IndexError! Smokie, go look at my logs now.';
      return (raw, error_speech)
    
  def clean_parentheses(self):
    # remove all parentheses-wrapped content in user messages, which are meant to be
    # instructions to llm rather than actual relevant chat history
    self.messages = [({
      'role': i['role'],
      'content': remove_text_inside_parentheses(i['content'])
    } if i['role'] == 'user' else i) for i in self.messages]

  def trim(self):
    # delete a fixed number of messages, to help appease token limits
    for i in range(4):
      if len(self.messages) > memory_trim_index:
        del self.messages[memory_trim_index]

  def erase_memory(self):
    self.messages = self.messages[:memory_trim_index]

  def load_initial_messages(self, db_messages):
    # db_messages is a list of MessageSchema dicts
    if len(db_messages) > 5:
      raise RuntimeError('Can\'t load more than 5 messages from memory, as a financial precaution.')
    for i in reversed(db_messages):
      self.add_user_message(i['prompt'])
      self.add_assistant_message(i['response'])
