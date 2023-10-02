import config
from time import sleep

def execute_or_enqueue_action(promptAndPriority):
  print(config.priority_queue.get_items())
  if config.is_busy:
    enqueue_action(promptAndPriority)
  else:
    execute_action(promptAndPriority)

def enqueue_action(promptAndPriority):
  config.priority_queue.enqueue(promptAndPriority)

def execute_action(promptAndPriority):
  config.is_busy = True

  prompt = promptAndPriority[0]
  while prompt != "":
    # gen_ai_response()
    # gen_audio_file_and_subtitles()
    # play_audio_file()
    sleep(3)
    print('executed action: ' + prompt)
    prompt = config.priority_queue.dequeue()

  config.is_busy = False
