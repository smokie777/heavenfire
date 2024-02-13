from pynput.keyboard import Key, Listener
import config

def pynput_on_press(key):
  if key == Key.ctrl_r:
    config.azure.is_listening = True
    config.azure.recognize_from_microphone()

def pynput_on_release(key):
  if key == Key.pause:
    return False

def r_ctrl_stt_run():
  # Collect events until released
  with Listener(on_press=pynput_on_press, on_release=pynput_on_release) as listener:
    listener.join()
