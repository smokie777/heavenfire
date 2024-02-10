import re

# replace the username in a prompt with "username", for privacy reasons
def obfuscate_prompt_username(s):
  # Regular expression to find substrings matching the pattern "user_name:"
  pattern = r"\b\w+:"  # \b is a word boundary, \w+ matches one or more word characters, and : is a literal colon
  return s if s.startswith('smokie_777') else ( # don't replace my username
    re.sub(pattern, lambda x: "username:" if x.group(0)[:-1].isidentifier() else x.group(0), s)
  )
