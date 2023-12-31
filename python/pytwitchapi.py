from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
from twitchAPI.pubsub import PubSub
from uuid import UUID
import asyncio
import os
from enums import AZURE_SPEAKING_STYLE_TAGS, VTS_EXPRESSIONS, PRIORITY_QUEUE_PRIORITIES, TWITCH_EVENTS
from execute_action import execute_or_enqueue_action
from vts_set_expression import vts_set_expression
from dotenv import load_dotenv; load_dotenv()
from utils import does_one_word_start_with_at
import json
import config

twitch = None
chat = None
pubsub = None

APP_ID = os.environ['TWITCH_APP_ID']
APP_SECRET = os.environ['TWITCH_APP_SECRET']
# APP_ID = os.environ['TWITCH_APP_ID_LUNA']
# APP_SECRET = os.environ['TWITCH_APP_SECRET_LUNA']
USER_SCOPE = [
  # chat
  AuthScope.CHAT_READ,
  AuthScope.CHAT_EDIT,
  # pubsub
  AuthScope.CHANNEL_READ_REDEMPTIONS,
  AuthScope.BITS_READ,
  AuthScope.CHANNEL_READ_SUBSCRIPTIONS
]
TARGET_CHANNEL = 'smokie_777'

async def pubsub_callback_listen_channel_points(uuid: UUID, data: dict) -> None:
  print(data)
  title = data['data']['redemption']['reward']['title']
  display_name = data['data']['redemption']['user']['display_name']

  if title == 'luna whisper':
    vts_set_expression(VTS_EXPRESSIONS['FLUSHED'])
    user_input = data['data']['redemption']['user_input']
    prompt = f'{AZURE_SPEAKING_STYLE_TAGS["WHISPERING"]}(Luna, please give a longer response than usual!) {display_name}: {user_input}'
    execute_or_enqueue_action(prompt, PRIORITY_QUEUE_PRIORITIES['PRIORITY_PUBSUB_EVENTS_QUEUE'
    ])
  elif title == 'luna rant':
    vts_set_expression(VTS_EXPRESSIONS['ANGRY'])
    user_input = data['data']['redemption']['user_input']
    prompt = f'Luna, please go on a really long and angry rant about the following topic: {user_input}!'
    execute_or_enqueue_action(prompt, PRIORITY_QUEUE_PRIORITIES['PRIORITY_PUBSUB_EVENTS_QUEUE'
    ])
  elif title == 'Luna brown hair':
    vts_set_expression(VTS_EXPRESSIONS['BROWN_HAIR'])

async def pubsub_callback_listen_bits_v1(uuid: UUID, data: dict) -> None:
  print(data)
  data = data.get('data')
  user_name = data.get('user_name')
  bits = data.get('bits_used')
  chat_message = data.get('chat_message')
  prompt = f'{user_name} just cheered {bits} bits! Their message: {chat_message}'
  # send bits data to websocket
  config.ws.send(json.dumps({
    'twitch_event': {
      'event': TWITCH_EVENTS['BITS'],
      'username': user_name,
      'value': str(bits)
    }
  }))
  execute_or_enqueue_action(prompt, PRIORITY_QUEUE_PRIORITIES['PRIORITY_PUBSUB_EVENTS_QUEUE'
  ])

async def pubsub_callback_listen_channel_subscriptions(uuid: UUID, data: dict) -> None:
  print(data)
  prompt = ''
  ws_sub_name = ''
  ws_message = ''
  display_name = data.get('display_name') if data.get('display_name') else 'An anonymous gifter'
  tier = 'Prime' if data.get('sub_plan') == 'Prime' else f'Tier {str((int(data.get("sub_plan")) // 1000))}'
  is_gift = data.get('is_gift')
  recipient_display_name = data.get('recipient_display_name')
  multi_month_duration = data.get('multi_month_duration')
  cumulative_months = data.get('cumulative_months')
  if is_gift:
    if multi_month_duration:
      ws_sub_name = display_name
      ws_message = f'gifted a {multi_month_duration}-month {tier} sub to {recipient_display_name}!'
      prompt = f'{ws_sub_name} just {ws_message}'
    else:
      ws_sub_name = display_name
      ws_message = f'gifted a {tier} sub to {recipient_display_name}!'
      prompt = f'{ws_sub_name} just {ws_message}'
  else:
    if multi_month_duration:
      prompt = f'{display_name} just bought a {multi_month_duration}-month {tier} sub!'
      ws_sub_name = display_name
      ws_message = f'{multi_month_duration}-month {tier} sub'
    elif cumulative_months > 1:
      prompt = f'{display_name} just resubscribed for {cumulative_months} months!'
      ws_sub_name = display_name
      ws_message = f'x{cumulative_months} resub'
    else:
      prompt = f'{display_name} just subscribed at {tier}!'
      ws_sub_name = display_name
      ws_message = f'{tier} sub'
  config.ws.send(json.dumps({
    'twitch_event': {
      'event': TWITCH_EVENTS['SUB'],
      'username': ws_sub_name,
      'value': ws_message
    }
  }))
  execute_or_enqueue_action(prompt, PRIORITY_QUEUE_PRIORITIES['PRIORITY_PUBSUB_EVENTS_QUEUE'
  ])

async def chat_on_ready(ready_event: EventData):
  print('pytwitchapi chat connected')
  await ready_event.chat.join_room(TARGET_CHANNEL)

async def chat_on_message(msg: ChatMessage):
  prompt = f'{msg.user.name}: {msg.text}'
  is_at_luna = '@luna' in msg.text.lower() or '@hellfire' in msg.text.lower()

  if (
    config.is_twitch_chat_react_on
    and msg.text[0] != '!'
    and msg.user.name != 'Streamlabs'
    and (
      (config.is_quiet_mode_on and is_at_luna)
      or (not config.is_quiet_mode_on and (is_at_luna or not does_one_word_start_with_at(msg.text.lower().split(' '))))
    )
  ):
    execute_or_enqueue_action(prompt, PRIORITY_QUEUE_PRIORITIES['PRIORITY_TWITCH_CHAT_QUEUE'
    ])

async def chat_on_command_discord(cmd: ChatCommand):
  await cmd.reply('https://discord.gg/cxTHwepMTb 🖤✨')

async def chat_on_command_profile(cmd: ChatCommand):
  await cmd.reply('https://www.pathofexile.com/account/view-profile/smokie_777/characters 🖤✨')

async def chat_on_command_pob(cmd: ChatCommand):
  await cmd.reply('https://pobb.in/rBu7TCkUjiRY 🖤✨')

async def chat_on_command_filter(cmd: ChatCommand):
  await cmd.reply('https://www.filterblade.xyz/Profile?name=kiteezy&platform=pc 🖤✨')

async def chat_on_command_video(cmd: ChatCommand):
  await cmd.reply('https://www.youtube.com/watch?v=in7lM9aoEn8 🖤✨')

async def terminate_pytwitchapi():
  chat.stop()
  pubsub.stop()
  await twitch.close()
    
async def run_pytwitchapi():
  global twitch
  global chat

  twitch = await Twitch(APP_ID, APP_SECRET)
  auth = UserAuthenticator(twitch, USER_SCOPE, force_verify=False)
  token, refresh_token = await auth.authenticate()
  await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)

  chat = await Chat(twitch)
  chat.register_event(ChatEvent.READY, chat_on_ready)
  chat.register_event(ChatEvent.MESSAGE, chat_on_message)
  chat.register_command('discord', chat_on_command_discord)
  chat.register_command('profile', chat_on_command_profile)
  chat.register_command('pob', chat_on_command_pob)
  chat.register_command('filter', chat_on_command_filter)
  chat.register_command('video', chat_on_command_video)
  chat.start()

  pubsub = PubSub(twitch)
  pubsub.start()
  await pubsub.listen_channel_points(
    str(os.environ['TWITCH_CHANNEL_ID']),
    pubsub_callback_listen_channel_points
  )
  await pubsub.listen_bits_v1(
    str(os.environ['TWITCH_CHANNEL_ID']),
    pubsub_callback_listen_bits_v1
  )
  await pubsub.listen_channel_subscriptions(
    str(os.environ['TWITCH_CHANNEL_ID']),
    pubsub_callback_listen_channel_subscriptions
  )


if __name__ == '__main__':
  # asyncio.run(run_pytwitchapi())

  # config.ws.send(json.dumps({
  #   'twitch_event': {
  #     'event': TWITCH_EVENTS['BITS'],
  #     'username': 'username1',
  #     'value': str(200)
  #   }
  # }))
  config.ws.send(json.dumps({
    'twitch_event': {
      'event': TWITCH_EVENTS['SUB'],
      'username': 'username2',
      'value': 'x3 resub'
    }
  }))
  # config.ws.send(json.dumps({
  #   'twitch_event': {
  #     'event': TWITCH_EVENTS['BAN'],
  #     'username': 'username3',
  #     'value': None
  #   }
  # }))
  