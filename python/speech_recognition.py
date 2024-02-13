import azure.cognitiveservices.speech as speechsdk
from pynput.keyboard import Key, Listener
from dotenv import load_dotenv; load_dotenv()
import os

# https://learn.microsoft.com/en-us/azure/ai-services/speech-service/get-started-speech-to-text?tabs=windows%2Cterminal&pivots=programming-language-python

speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
speech_config.speech_recognition_language="en-US"

audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

is_listening = False

def azure_recognize_from_microphone():
  global is_listening

  if not is_listening:
    return
  
  print("Speak into your microphone.")
  speech_recognition_result = speech_recognizer.recognize_once_async().get()

  if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
    print("Recognized: {}".format(speech_recognition_result.text))
  elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
    print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
  elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = speech_recognition_result.cancellation_details
    print("Speech Recognition canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
      print("Error details: {}".format(cancellation_details.error_details))
      print("Did you set the speech resource key and region values?")

  is_listening = False

def pynput_on_press(key):
  global is_listening

  if key == Key.ctrl_r:
    is_listening = True
    azure_recognize_from_microphone()


def pynput_on_release(key):
  if key == Key.pause:
    return False

# Collect events until released
with Listener(on_press=pynput_on_press, on_release=pynput_on_release) as listener:
  listener.join()
