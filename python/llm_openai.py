import os
import config
import openai
from dotenv import load_dotenv; load_dotenv()
from LLMShortTermMemory import generate_base_messages

openai.api_key = os.environ['OPENAI_KEY']

def gen_llm_response(prompt):
  if not prompt:
    return ''

  if len(prompt) > 1500:
    prompt = 'You\'ve received a message that\'s way too long, and is probably spam! Inform Smokie about it.'
  
  config.llm_short_term_memory.add_user_message(prompt)

  chat = openai.ChatCompletion.create(
    # model = os.environ['LUNA_GPT_MODEL_CHEAP'],
    # model = os.environ['LUNA_GPT_MODEL_EXPENSIVE'],
    model = os.environ['LUNA_GPT_MODEL_FINETUNED'],
    # model = os.environ['LUNA_GPT_MODEL_FINETUNED_2'],
    messages=config.llm_short_term_memory.messages,
    temperature=float(os.environ['LUNA_GPT_TEMPERATURE']),
    presence_penalty=float(os.environ['LUNA_GPT_PRESENCE_PENALTY']),
    frequency_penalty=float(os.environ['LUNA_GPT_FREQUENCY_PENALTY']),
    max_tokens=int(os.environ['LUNA_GPT_MAX_TOKENS'])
    # ^parameters explained: https://platform.openai.com/docs/api-reference/chat/create
  )

  reply = chat.choices[0].message.content

  total_tokens = chat.usage.total_tokens
  
  print('-> TOTAL TOKENS: ', total_tokens)
  
  raw, edited = config.llm_short_term_memory.add_assistant_message(reply)

  config.llm_short_term_memory.clean_parentheses()

  if total_tokens > config.llm_fuzzy_token_limit:
    config.llm_short_term_memory.trim()

  # print('-> MESSAGES: ', config.llm_short_term_memory.messages[1:])

  return (prompt, raw, edited)
  

if __name__ == '__main__':
  m = messages = [{ 'role': 'system', 'content': '' }]
  m.append(
    { 'role': 'user', 'content': 'In one line, list 1-3 random keywords that could be used to start a conversation. For example: "Bagels", "The other day", "Don\'t you hate it when"' }
  )
  chat = openai.ChatCompletion.create(
    # model = os.environ['LUNA_GPT_MODEL_CHEAP'],
    # model = os.environ['LUNA_GPT_MODEL_EXPENSIVE'],
    # model = os.environ['LUNA_GPT_MODEL_FINETUNED'],
    model = os.environ['LUNA_GPT_MODEL_FINETUNED_2'],
    messages=m,
    temperature=float(1),
    presence_penalty=float(0),
    frequency_penalty=float(0),
    max_tokens=int(os.environ['LUNA_GPT_MAX_TOKENS'])
    # ^parameters explained: https://platform.openai.com/docs/api-reference/chat/create
  )

  reply = chat.choices[0].message.content

  print(reply)