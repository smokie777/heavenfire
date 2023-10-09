from prompts import system, system_extra
from utils import remove_text_inside_parentheses, move_emojis_to_end

def generate_base_messages():
  return [
    {
      'role': 'system',
      'content': system + ' ' + system_extra
    }
  ]

class LLMShortTermMemory:
  def __init__(self):
    self.messages = generate_base_messages()

  def add_user_message(self, content):
    self.messages.append({ 'role': 'user', 'content': content })

  def add_assistant_message(self, content):
    edited = move_emojis_to_end(content)

    print('Raw: ', content)
    print('Edited: ', edited)
    
    self.messages.append({
      'role': 'assistant',
      'content': edited
    })

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
      if len(self.messages) > 1:
        del self.messages[1]

  def erase_memory(self):
    self.messages = generate_base_messages()


if __name__ == '__main__':
  print('hello world')
