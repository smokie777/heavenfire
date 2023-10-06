import sys; sys.path.append('../server')
import os
import config
from dotenv import load_dotenv; load_dotenv()

def gen_ai_response(prompt):
  print(config.llm_short_term_memory)


if __name__ == '__main__':
  gen_ai_response('foo')
