import requests
from dotenv import load_dotenv; load_dotenv()
import os
from tts import gen_output_filename

CHUNK_SIZE = 1024

url = f'https://api.elevenlabs.io/v1/text-to-speech/{os.environ["ELEVEN_LABS_VOICE_ID_SMOKIE_VOICE_CLONE"]}'

querystring = { 'output_format': 'mp3_44100_192' }

headers = {
  'xi-api-key': os.environ['ELEVEN_LABS_API_KEY'],
  'Content-Type': 'application/json'
}

def eleven_labs_tts_speak(text):
  if len(text) > 500:
    return
  
  print('eleven_labs_tts_speak', text)
  payload = {
    'text': text,
    'voice_settings': {
      'use_speaker_boost': True,
      'style': 0,
      'stability': 1,
      'similarity_boost': 0.75
    },
    'model_id': 'eleven_multilingual_v2'
  }

  response = requests.request('POST', url, json=payload, headers=headers, params=querystring)

  output_file_name = gen_output_filename() + '_elevenlabs.mp3'

  with open(output_file_name, 'wb') as f:
    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
      if chunk:
        f.write(chunk)

    os.startfile(os.path.abspath(output_file_name))


if __name__ == '__main__':
  eleven_labs_tts_speak("Urgh, Smokie. I'm not a puppet. If you want me to say something, just ask!")
  