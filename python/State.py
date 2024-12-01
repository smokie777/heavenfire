# centralized state

# this class uses the singleton pattern to avoid multiple instantiations
class StateClass:
  _instance = None

  def __new__(cls, *args, **kwargs):
    if cls._instance is None:
      cls._instance = super(StateClass, cls).__new__(cls, *args, **kwargs)
      cls._instance.__initialize()
      return cls._instance

  def __initialize(self):
    # the vtuber can't perform any actions while is_busy is True.
    self.is_busy = False
    # llm fuzzy token limit
    self.llm_fuzzy_token_limit = 750
    # make this false for a couple seconds to terminate the audio playing loop.
    self.tts_green_light = True
    # seconds of delay bewteen ai responses
    self.ai_response_delay = 2.5
    # is the vtuber responding to twitch chat?
    self.is_twitch_chat_react_on = True
    # is the vtuber responding to twitch chat, but only if @ mentioned?
    self.is_quiet_mode_on = True
    # is singing in action
    self.is_singing = False

    # stores tuples like ('remind foo to bar!', datetime)
    self.remind_me_prompts_and_datetime_queue = []
    # stores raffle entries
    self.raffle_entries_set = set()
    
    print('[CONFIG] Initialized State.')


State = StateClass()
