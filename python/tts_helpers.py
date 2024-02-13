import pyaudio
from datetime import datetime
import os
import contextlib
import wave

def get_pyaudio_output_audio_index():
  p = pyaudio.PyAudio()
  output_device_name = 'CABLE Input' # for production
  # output_device_name = 'Speakers' # for development
  # output_device_name = 'Headphones' # for development
  # output_device_name = 'Built-in Output' # for development on macbook
  devices = [p.get_device_info_by_index(i).get('name') for i in range(p.get_device_count())]
  output_device_index = [i for i, s in enumerate(devices) if output_device_name in s][0]
  return output_device_index

def gen_output_audio_filename():
  # returned filename does not include file extension, such as .mp3 or .wav
  now = datetime.now()
  date_time = now.strftime('%m-%d-%Y_%H-%M-%S')
  filename = f'./output_audio_files/output{date_time}'
  return filename

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
