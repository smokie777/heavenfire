class Prompt:
  def __init__(
    self,
    prompt,
    priority,
    utterance_id = None,
    azure_speaking_style = None,
    username_to_ban = None,
    is_eleven_labs = False,
    should_generate_audio_file_only = False,
    pytwitchapi_args = {}
  ):
    self.prompt = prompt
    self.priority = priority
    self.utterance_id = utterance_id
    self.azure_speaking_style = azure_speaking_style
    self.username_to_ban = username_to_ban
    self.is_eleven_labs = is_eleven_labs
    self.should_generate_audio_file_only = should_generate_audio_file_only
    self.pytwitchapi_args = pytwitchapi_args
    