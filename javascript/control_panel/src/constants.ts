// how long to wait before sending mic input as a complete block
export const MIC_INPUT_DELAY = 0;

export const priority_queue_map = {
  'priority_pubsub_events_queue': 1,
  'priority_mic_input': 2,
  'priority_collab_mic_input': 3,
  'priority_image': 4,
  'priority_twitch_chat_queue': 5,
};
