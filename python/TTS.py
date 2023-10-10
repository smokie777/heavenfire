import os
import requests
from pydub import AudioSegment
from datetime import datetime
import pyaudio
import wave
import azure.cognitiveservices.speech as speechsdk
from threading import Thread
import contextlib
import emoji
import re
import config
from dotenv import load_dotenv; load_dotenv()

# HOW TO PREPARE AZURE SSML
# 1. copy ssml from azure
# 2. replace <prosody /> with %PROSODY_SSML% 
# 3. refactor it to be one line
# 4. wrap it in single quotes '', and put it in .env

def get_output_audio_index():
  p = pyaudio.PyAudio()
  output_device_name = 'CABLE Input' # for production
  # output_device_name = 'Speakers' # for development
  # output_device_name = 'Headphones' # for development
  devices = [p.get_device_info_by_index(i).get('name') for i in range(p.get_device_count())] 
  output_device_index = [i for i, s in enumerate(devices) if output_device_name in s][0]
  return output_device_index

word_offsets = []

OUTPUT_AUDIO_INDEX = get_output_audio_index()
AZURE_POST_URL = 'https://{0}.tts.speech.microsoft.com/cognitiveservices/v1'.format(
  os.environ['SPEECH_REGION']
)
AZURE_POST_HEADERS = {
  'Ocp-Apim-Subscription-Key': os.environ['SPEECH_KEY'],
  'Content-Type': 'application/ssml+xml; charset=utf-8',
  'X-Microsoft-OutputFormat': 'audio-48khz-192kbitrate-mono-mp3'
  # 'X-Microsoft-OutputFormat': 'audio-48khz-96kbitrate-mono-mp3'
}
SPEECHSDK_SPEECH_CONFIG = speechsdk.SpeechConfig(
  subscription=os.environ.get('SPEECH_KEY'),
  region=os.environ.get('SPEECH_REGION')
)
# intentionally use a low quality output, to save money on subtitle generation
SPEECHSDK_SPEECH_CONFIG.set_speech_synthesis_output_format(
  speechsdk.SpeechSynthesisOutputFormat.Raw8Khz8BitMonoMULaw
)
SPEECHSDK_SPEECH_SYNTHESIZER = speechsdk.SpeechSynthesizer(
  speech_config=SPEECHSDK_SPEECH_CONFIG,
  audio_config=None
)
SPEECHSDK_SPEECH_SYNTHESIZER.synthesis_word_boundary.connect(
  lambda evt: word_offsets.append({
    'text_offset': evt.text_offset, # the start index of the spoken word in the complete text string
    'audio_offset': evt.audio_offset / 10000 # the time in ms it took to say the word
  })
)

def gen_output_filename():
  # returned filename does not include file extension, such as .mp3 or .wav
  now = datetime.now()
  date_time = now.strftime('%m-%d-%Y_%H-%M-%S')
  filename = f'./output_audio_files/output{date_time}'
  return filename

def _gen_audio_file_thread(ssml, store):
  response = requests.post(
    url=AZURE_POST_URL,
    data=ssml.encode('utf-8'),
    headers=AZURE_POST_HEADERS
  )
  output_filename = gen_output_filename()
  f = open(output_filename + '.mp3', 'wb')
  f.write(response.content)
  # convert to wav. if you don't do this, there is difficulty playing the .mp3 file
  sound = AudioSegment.from_mp3(output_filename + '.mp3')
  sound.export(output_filename + '.wav', format='wav')
  store['output_filename'] = output_filename + '.wav'

def _gen_subtitles_thread(ssml, store):
  global word_offsets
  word_offsets = []
  SPEECHSDK_SPEECH_SYNTHESIZER.speak_ssml_async(ssml).get()
  store['subtitles'] = word_offsets

def gen_audio_file_and_subtitles(text, speaking_style = '', skipGeneratingSubtitles = False):
  # note: this function calls the speech API twice, once using REST, and once using speechsdk.
  # this is necessary because only speechsdk can give word timestamps, but unfortunately
  # speechsdk only allows saving ssml generated audio as a converted wav,
  # and speechsdk's built-in wav converter causes a tremendous loss in audio quality.
  # therefore, we get only word timestamps from speechsdk, and the high quality audio we get from REST.

  # replace emojis with text representations so tts can say them
  # this below line is chatgpt generated code that converts emojis to ':emoji_text:' to 'emoji text'.
  emoji_processed_text = re.sub(
    r':(\w+):',
    lambda m: m.group(1).replace('_', ' '),
    emoji.demojize(text)
  )

  prosody_ssml = '<prosody pitch="+10.00%">' + emoji_processed_text + '</prosody>'
  if speaking_style:
    prosody_ssml = '<mstts:express-as style="' + speaking_style + '">' + prosody_ssml + '</mstts:express-as>'

  ssml = os.environ['LUNA_AZURE_SSML'].replace('%PROSODY_SSML%', prosody_ssml)

  # utilize threading, so that both API calls happen simultaneously
  store = {
    'output_filename': '',
    'subtitles': []
  }
  threads = [
    Thread(target=_gen_audio_file_thread, args=(ssml, store))
  ]
  if not skipGeneratingSubtitles:
    threads.append(Thread(target=_gen_subtitles_thread, args=(ssml, store)))
  [t.start() for t in threads]
  [t.join() for t in threads]

  return (store['output_filename'], store['subtitles'])

def speak(output_filename):
  wf = wave.open(output_filename, 'rb')
  p = pyaudio.PyAudio()
  chunk = 1024
  stream = p.open(
    format=p.get_format_from_width(wf.getsampwidth()),
    channels=wf.getnchannels(),
    rate=wf.getframerate(),
    output=True,
    output_device_index=OUTPUT_AUDIO_INDEX # play the wav file through virtual cable input
  )
  data = wf.readframes(chunk)
  while len(data) > 0:
    if config.tts_green_light:
      stream.write(data)
      data = wf.readframes(chunk)
    else:
      break
  stream.close()
  p.terminate()
  
def cleanup_wav_files():
  # delete temporary & closed audio files
  # return
  for file in [i for i in os.listdir('./output_audio_files') if '.wav' in i]:
    try:
      os.remove('./output_audio_files/' + file)
    except:
      True

def cleanup_mp3_files():
  # delete temporary & closed audio files
  # return
  for file in [i for i in os.listdir('./output_audio_files') if '.mp3' in i]:
    try:
      os.remove('./output_audio_files/' + file)
    except:
      True

def print_wav_length(filename):
  with contextlib.closing(wave.open(filename, 'r')) as f:
    frames = f.getnframes()
    rate = f.getframerate()
    duration = frames / float(rate)
    print('--> ' + str(duration) + 's')

if __name__ == '__main__':
  s = "Luna's streams are like a wild rollercoaster ride 🎢🔥, filled with laughter 😂, surprises ✨, and moments that will make your heart skip a beat 💖."
  store = gen_audio_file_and_subtitles(s)
  print(store)
