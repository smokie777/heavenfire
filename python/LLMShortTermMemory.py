from prompts import system
from utils import remove_text_inside_parentheses, move_emojis_to_end
from gen_edited_luna_response import gen_edited_luna_response

def generate_base_messages(context):
  return [
    { 'role': 'system', 'content': system },
    { 'role': 'user', 'content': f'Today\'s context: {context}' },
    { 'role': 'assistant', 'content': 'Got it!' },
  ]

memory_trim_index = len(generate_base_messages(''))

class LLMShortTermMemory:
  def __init__(self, context):
    self.messages = generate_base_messages(context)

  def add_user_message(self, content):
    self.messages.append({ 'role': 'user', 'content': content })

  def add_assistant_message(self, content):
    raw = content
    try:
      edited = move_emojis_to_end(gen_edited_luna_response(content))
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


if __name__ == '__main__':
  print('hello world')
