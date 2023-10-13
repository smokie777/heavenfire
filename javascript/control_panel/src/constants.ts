// how long to wait before sending mic input as a complete block
export const MIC_INPUT_DELAY = 0;

export const PRIORITY_QUEUE_MAP = {
  'priority_game_input': 1,
  'priority_pubsub_events_queue': 2,
  'priority_mic_input': 3,
  'priority_collab_mic_input': 4,
  'priority_image': 5,
  'priority_twitch_chat_queue': 6,
};
