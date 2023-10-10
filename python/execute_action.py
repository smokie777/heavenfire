import config
from time import sleep
from gen_llm_response import gen_llm_response
from tts import gen_audio_file_and_subtitles, speak

def execute_or_enqueue_action(promptAndPriority):
  if config.is_busy:
    enqueue_action(promptAndPriority)
  else:
    execute_action(promptAndPriority)

def enqueue_action(promptAndPriority):
  config.priority_queue.enqueue(promptAndPriority)

def execute_action(promptAndPriority):
  config.is_busy = True

  prompt = promptAndPriority[0]
  while prompt != '':
    print(1)
    (prompt, raw, edited) = gen_llm_response(prompt)
    print('Prompt: ', prompt)
    print('Raw: ', raw)
    print('Edited: ', edited)
    # send (prompt, raw, edited) to websocket
    (output_filename, subtitles) = gen_audio_file_and_subtitles(edited)
    # send subtitles to websocket
    speak(output_filename)
    
    prompt = config.priority_queue.dequeue()

  config.is_busy = False


if __name__ == '__main__':
  execute_action(('test prompt.', 1))
