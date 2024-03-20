import os
import config
import openai
from dotenv import load_dotenv; load_dotenv()

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
    # temperature=2,
    presence_penalty=float(os.environ['LUNA_GPT_PRESENCE_PENALTY']),
    frequency_penalty=float(os.environ['LUNA_GPT_FREQUENCY_PENALTY']),
    max_tokens=int(os.environ['LUNA_GPT_MAX_TOKENS'])
    # ^parameters explained: https://platform.openai.com/docs/api-reference/chat/create
  )

  reply = chat.choices[0].message.content

  # # custom !timeout functionality
  # if '!timeout' in reply:
  #   original_reply = reply
  #   chat = openai.ChatCompletion.create(
  #     model = os.environ['LUNA_GPT_MODEL_CHEAP'],
  #     # model = os.environ['LUNA_GPT_MODEL_EXPENSIVE'],
  #     # model = os.environ['LUNA_GPT_MODEL_FINETUNED'],
  #     # model = os.environ['LUNA_GPT_MODEL_FINETUNED_2'],
  #     messages=[
  #       { 'role': 'system', 'content': 'You are helping an AI VTuber on Twitch generate responses to time people out. You can timeout users by saying, !timeout username. Refactor the given response to utilize the !timeout command.' },
  #       { 'role': 'user', 'content': reply }
  #     ],
  #     temperature=float(os.environ['LUNA_GPT_TEMPERATURE']),
  #     # temperature=2,
  #     presence_penalty=float(os.environ['LUNA_GPT_PRESENCE_PENALTY']),
  #     frequency_penalty=float(os.environ['LUNA_GPT_FREQUENCY_PENALTY']),
  #     max_tokens=int(os.environ['LUNA_GPT_MAX_TOKENS'])
  #     # ^parameters explained: https://platform.openai.com/docs/api-reference/chat/create
  #   )
  #   reply = chat.choices[0].message.content
  #   print(f'[LLM] !timeout override used. Original reply: {original_reply}')

  total_tokens = chat.usage.total_tokens
  
  print('[LLM] TOTAL TOKENS: ', total_tokens)
  
  raw, edited = config.llm_short_term_memory.add_assistant_message(reply)

  config.llm_short_term_memory.clean_parentheses()

  if total_tokens > config.llm_fuzzy_token_limit:
    config.llm_short_term_memory.trim()
    
  return (prompt, raw, edited)
