punctuation_characters = { '.', ',', '-', '~', '!', '?', '\'', '"', ':', '+', '=', '<', '>', '[', ']', '{', '}', '|', '\\', '/', ';', ')', '(', '*', '&', '^', '%', '$', '#', '@', '`' }

laugh_abbreviations = ['lol', 'lmao', 'rofl', 'roflmao', 'rotfl']

def contains_only_letter(s, letter):
  for i in s:
    if i != letter:
      return False

  return True

def is_mouth_sound(s, letter1, letter2, exceptions=[]):
  if (
    not s 
    or s in exceptions
    or s == letter1 or s == letter2
    or letter1 not in s or letter2 not in s
  ):
    return False

  for i in range(len(s)):
    if s[i] == letter2:
      if contains_only_letter(s[i:], letter2):
        return True
      else:
        return False
    elif s[i] != letter1:
      return False

  return True

def split_punctuation(s):
  text = ''
  punctuation = ''

  for i in s:
    if i in punctuation_characters:
      punctuation += i
    else:
      text += i
        
  return (text, punctuation)

def strip_leading_letters(s, letter):
  for i in range(len(s)):
    if s[i] != letter:
      return s[i:]

  return ''

def is_uppercase(s):
  # the lower() logic prevents non-alphabetical strings like '1234' from being recognized as uppercase
  return s == s.upper() and s != s.lower()

def process_text_emojis(s):
  words = s.split()

  for idx, word in enumerate(words):
    lowercase_word = word.lower()

    if is_mouth_sound(lowercase_word, ':', '('):
      words[idx] = '=('
    elif is_mouth_sound(lowercase_word, ':', ')'):
      words[idx] = '=)'
    elif is_mouth_sound(lowercase_word, ':', 'p'):
      words[idx] = '=P'
    elif is_mouth_sound(lowercase_word, ':', 'o'):
      words[idx] = ':0'

  return ' '.join(words)

replacements = [
  ('Oh no', 'Oh, no...'),
  ('oh no', 'oh, no...'),
  ('OH NO', 'OH, NO...'),
  ('see ya', 'see you'),
  ('See ya', 'See you'),
  ('SEE YA', 'SEE YOU'),
  ('Yeah', 'Yea'),
  ('yeah', 'yea'),
  ('&', 'N'),
  ('—', '-'),
  (':(', '=('),
  (':)', '=)'),
  (':p', '=P'),
  (':o', ':0'),
  (';)', '*wink*'),
  ('Duuude', 'Dude'),
  ('Duude', 'Dude')
]

def gen_edited_luna_response(s):
  s = s.replace('..', '...')
  words = (process_text_emojis(s)).replace('...', '... ').split()
  processed_words = []
  
  for word in words:
    text, punctuation = split_punctuation(word.lower())
    replacement_word = ''

    if 'haha' in text:
      replacement_word = text.replace('haha', 'ahaha')
    if 'hehe' in text:
      replacement_word = text.replace('hehe', 'heehee')
    if text in ['hah', 'heh'] or 'ahaha' in text:
      replacement_word = 'ahaha'
    elif text == 'loots':
      replacement_word = 'loot'
    elif text in laugh_abbreviations:
      replacement_word = ' '.join([c.upper() for c in text]) + (punctuation[-1] if punctuation else '')
    elif text == 'xd':
      replacement_word = 'xDD'
    elif 'uhoh' in text:
      replacement_word = 'Oops'
    elif 'bye' in text and text != 'lobbyers' and 'rockabye' not in text:
      replacement_word = 'See you later'
    elif is_mouth_sound(text, 'h', 'a'):
      replacement_word = 'Ahaha'
    elif is_mouth_sound(text, 'a', 'h') or is_mouth_sound(text, 'o', 'h', ['oh']):
      replacement_word = 'Oh'
    elif is_mouth_sound(strip_leading_letters(text, 'n'), 'a', 'h') and text.startswith('n'):
      replacement_word = 'Nope'
    elif is_mouth_sound(text, 'o', 'o', ['oo']):
      replacement_word = 'Oo'
    elif is_mouth_sound(text, 'a', 'a'):
      replacement_word = 'Aa'
    elif is_mouth_sound(text, 'e', 'e'):
      replacement_word = 'Ee'
    elif (
      is_mouth_sound(text, 'e', 'r')
      or is_mouth_sound(text, 'u', 'm')
      or is_mouth_sound(text, 'u', 'h')
      or 'uhuh' in text
    ):
      replacement_word = 'Erm'
    elif is_mouth_sound(strip_leading_letters(text, 'd'), 'u', 'h'):
      replacement_word = 'Obviously'
    elif is_mouth_sound(text, 'm', 'm') or is_mouth_sound(text, 'h', 'm'):
      replacement_word = 'Mm'
    elif is_mouth_sound(strip_leading_letters(text, 'm'), 'e', 'h'):
      replacement_word = 'Eh'
    elif is_mouth_sound(text, 'a', 'y', ['ay']):
      replacement_word = 'Ay'
    elif is_mouth_sound(text, 'z', 'z', ['zz']):
      replacement_word = 'zz'
    elif is_mouth_sound(text, 'a', 'w'):
      replacement_word = 'Awh'
    elif is_mouth_sound(strip_leading_letters(text, 'y'), 'a', 'y'):
      replacement_word = 'Hooray'
    elif is_mouth_sound(strip_leading_letters(text, 'y'), 'o', 'u'):
      replacement_word = 'You'
    elif is_mouth_sound(strip_leading_letters(text, 'h'), 'e', 'y'):
      replacement_word = 'Hey'
    elif is_mouth_sound(strip_leading_letters(text, 'p'), 'f', 't'):
      replacement_word = 'Wow'
    elif is_mouth_sound(strip_leading_letters(text, 'y'), 'a', 's', ['yas', 'as', 'ass']):
      replacement_word = 'Yas'
    elif is_mouth_sound(strip_leading_letters(text, 'y'), 'e', 's', ['yes', 'es']):
      replacement_word = 'Yes'
    elif is_mouth_sound(text, 'd', 'o', ['do']):
      replacement_word = 'Do'
    elif is_mouth_sound(text, 'y', 'o', ['yo']):
      replacement_word = 'Yo'
    elif is_mouth_sound(text, 'g', 'o', ['go']):
      replacement_word = 'Go'
    elif is_mouth_sound(text, 'b', 'o', ['bo', 'boo']):
      replacement_word = 'Boo'
    elif is_mouth_sound(text, 's', 'o', ['so']):
      replacement_word = 'So'
    elif is_mouth_sound(text, 'n', 'o', ['no']):
      replacement_word = 'No'
    elif is_mouth_sound(text, 'y', 'e', ['ye']):
      replacement_word = 'Ye'
    elif is_mouth_sound(text, 's', 'h', []):
      replacement_word = 'Be quiet'
    elif is_mouth_sound(text, 'e', 'w') or is_mouth_sound(strip_leading_letters(text, 'u'), 'g', 'h'):
      replacement_word = 'Urgh'
    elif is_mouth_sound(strip_leading_letters(strip_leading_letters(text, 'y'), 'e'), 'a', 'h'):
      replacement_word = 'Yea'
    elif is_mouth_sound(
      strip_leading_letters(strip_leading_letters(strip_leading_letters(text, 'y'), 'e'),  'h'), 'a', 'w'
    ):
      replacement_word = 'yeehaw'

    if replacement_word:
      original_case_text, _ = split_punctuation(word)
      if original_case_text:
        processed_words.append(
          (replacement_word[0].upper() if original_case_text[0].isupper() else replacement_word[0].lower())
          + replacement_word[1:]
          + (punctuation if punctuation == '...' else (punctuation[-1] if punctuation else ''))
        )
      else:
        processed_words.append(word)  
    else:    
      processed_words.append(word)

  ret = ' '.join(processed_words)

  for old, new in replacements:
    ret = ret.replace(old, new)
  
  if ret.startswith('"') and ret.endswith('"'):
    ret = ret[1:-1]

  return ret.replace('... ', '...')

if __name__ == '__main__':
  print(gen_edited_luna_response('Umm...Smokie? Testing?'))
