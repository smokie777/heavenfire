import os
from time import sleep
import multiprocessing
import config

# STEPS TO MAKE A SONG
# 1. Obtain high quality instrumental track & acapella
# 2. Run RVC on the acapella. Save the result as song_v.wav in /songs
# 3. Use Audacity to combine the instrumental & the RVC acapella. Save result as song_iv.wav in .songs
# 4. IMPORTANT: In Streamlabs, turn off virtual cable input, turn off mic, and turn on media player. In VTube studio, turn off audio preview.
# 5. Type the song name ("song" in this example) in the control panel textbox, and press "Sing".

# example: edamame_iv.wav is the full song, to be played through computer speakers.
def play_iv(song):
  sleep(0.3)
  os.startfile(os.path.abspath(f'./songs/{song}_iv.wav'))

# example: edamame_v.wav is the vocals only, to be played silently through the virtual cable
def play_v(song, azure_instance):
  azure_instance.speak(f'./songs/{song}_v.wav')
  config.is_singing = False

def sing(song, azure_instance):
  config.is_singing = True

  p1 = multiprocessing.Process(target=play_iv, args=(song,))
  p2 = multiprocessing.Process(target=play_v, args=(song, azure_instance,))

  p1.start()
  p2.start()

  p1.join()
  p2.join()
