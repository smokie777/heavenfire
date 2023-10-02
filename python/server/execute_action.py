import config

def execute_or_enqueue_action(promptAndPriority):
  if config.is_busy:
    enqueue_action(promptAndPriority)
  else:
    prompt
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
    print('executed action: ' + prompt)
    prompt = config.priority_queue.dequeue()

  config.is_busy = False
