import os
import requests
from pydub import AudioSegment
import pyaudio
import wave
import azure.cognitiveservices.speech as speechsdk
from threading import Thread
import emoji
import re
import config
from dotenv import load_dotenv; load_dotenv()
from tts_helpers import get_pyaudio_output_audio_index, gen_output_audio_filename
from enums import PRIORITY_QUEUE_PRIORITIES
# https://learn.microsoft.com/en-us/azure/ai-services/speech-service/get-started-speech-to-text?tabs=windows%2Cterminal&pivots=programming-language-python

class Azure:
  # TTS
  OUTPUT_AUDIO_INDEX = get_pyaudio_output_audio_index()
  AZURE_POST_URL = f'https://{os.environ["SPEECH_REGION"]}.tts.speech.microsoft.com/cognitiveservices/v1'
  AZURE_POST_HEADERS = {
    'Ocp-Apim-Subscription-Key': os.environ['SPEECH_KEY'],
    'Content-Type': 'application/ssml+xml; charset=utf-8',
    # 'X-Microsoft-OutputFormat': 'audio-48khz-192kbitrate-mono-mp3'
    'X-Microsoft-OutputFormat': 'audio-48khz-96kbitrate-mono-mp3'
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

  # STT
  SPEECHSDK_SPEECH_CONFIG.speech_recognition_language='en-US'
  AUDIO_CONFIG = speechsdk.audio.AudioConfig(use_default_microphone=True)
  SPEECH_RECOGNIZER = speechsdk.SpeechRecognizer(
    speech_config=SPEECHSDK_SPEECH_CONFIG,
    audio_config=AUDIO_CONFIG
  )

  def __init__(self):
    self.word_offsets = []
    self.is_listening = False

    self.SPEECHSDK_SPEECH_SYNTHESIZER.synthesis_word_boundary.connect(
      lambda evt: self.word_offsets.append({
        'text_offset': evt.text_offset, # the start index of the spoken word in the complete text string
        'audio_offset': evt.audio_offset / 10000 # the time in ms it took to say the word
      })
    )

  def _gen_audio_file_thread(self, ssml, store):
    response = requests.post(
      url=self.AZURE_POST_URL,
      data=ssml.encode('utf-8'),
      headers=self.AZURE_POST_HEADERS
    )
    output_filename = gen_output_audio_filename()
    f = open(output_filename + '.mp3', 'wb')
    f.write(response.content)
    # convert to wav. if you don't do this, there is difficulty playing the .mp3 file
    sound = AudioSegment.from_mp3(output_filename + '.mp3')
    sound.export(output_filename + '.wav', format='wav')
    store['output_filename'] = output_filename + '.wav'

  def _gen_subtitles_thread(self, ssml, store):
    self.word_offsets = []
    self.SPEECHSDK_SPEECH_SYNTHESIZER.speak_ssml_async(ssml).get()
    store['subtitles'] = self.word_offsets

  def gen_audio_file_and_subtitles(self, text, speaking_style = '', skipGeneratingSubtitles = False):
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

    # HOW TO PREPARE AZURE SSML
    # 1. copy ssml from azure
    # 2. replace <prosody /> with %PROSODY_SSML% 
    # 3. refactor it to be one line
    # 4. wrap it in single quotes '', and put it in .env
    prosody_ssml = '<prosody pitch="+10.00%">' + emoji_processed_text + '</prosody>'
    # prosody_ssml = '<prosody pitch="+10.00%"><say-as interpret-as="message">' + emoji_processed_text + '</say-as></prosody>'
    if speaking_style:
      prosody_ssml = '<mstts:express-as style="' + speaking_style + '">' + prosody_ssml + '</mstts:express-as>'

    ssml = os.environ['LUNA_AZURE_SSML'].replace('%PROSODY_SSML%', prosody_ssml)

    # utilize threading, so that both API calls happen simultaneously
    store = {
      'output_filename': '',
      'subtitles': []
    }
    threads = [
      Thread(target=self._gen_audio_file_thread, args=(ssml, store))
    ]
    if not skipGeneratingSubtitles:
      threads.append(Thread(target=self._gen_subtitles_thread, args=(ssml, store)))
    [t.start() for t in threads]
    [t.join() for t in threads]

    return (store['output_filename'], store['subtitles'])

  def speak(self, output_filename):
    wf = wave.open(output_filename, 'rb')
    p = pyaudio.PyAudio()
    chunk = 1024
    stream = p.open(
      format=p.get_format_from_width(wf.getsampwidth()),
      channels=wf.getnchannels(),
      rate=wf.getframerate(),
      output=True,
      output_device_index=self.OUTPUT_AUDIO_INDEX # play the wav file through virtual cable input
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
  
  def recognize_from_microphone(self):
    if not self.is_listening:
      return
    
    print('[STT] Listening to microphone...')
    speech_recognition_result = self.SPEECH_RECOGNIZER.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
      cleaned_mic_input = ' '.join(
        map(
          lambda i: 'Smokie' if i.lower() in ['smoky', 'smokey'] else i,
          map(
            lambda i: 'Luna' if i.lower() in ['lin', 'lena', 'linda', 'elena', 'lana'] else i,
            speech_recognition_result.text.split(' ')
          )
        )
      )
      print(f'[STT] Recognized: {cleaned_mic_input}')
      requests.post(
        'http://localhost:5001/receive_prompt',
        json={
          'prompt': f'Smokie: {cleaned_mic_input}',
          'priority': PRIORITY_QUEUE_PRIORITIES['PRIORITY_MIC_INPUT']
        }
      )
      # execute_or_enqueue_action(
      #   prompt=f'Smokie: {cleaned_mic_input}',
      #   priority=PRIORITY_QUEUE_PRIORITIES['PRIORITY_MIC_INPUT']
      # )
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
      print(f'[STT] Could not recognize speech: {speech_recognition_result.no_match_details}')
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
      cancellation_details = speech_recognition_result.cancellation_details
      print('[STT] Speech Recognition canceled: {cancellation_details.reason}')
      if cancellation_details.reason == speechsdk.CancellationReason.Error:
        print(f'[STT] Error details: {cancellation_details.error_details}')
        print('[STT] Did you set the speech resource key and region values?')

    self.is_listening = False
