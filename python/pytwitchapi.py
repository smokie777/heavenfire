from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatCommand
from twitchAPI.pubsub import PubSub
from uuid import UUID
import os
from enums import AZURE_SPEAKING_STYLE, VTS_EXPRESSIONS, PRIORITY_QUEUE_PRIORITIES, TWITCH_EVENTS, TWITCH_EVENT_TYPE
from vts_set_expression import vts_set_expression
from dotenv import load_dotenv; load_dotenv()
from utils import does_one_word_start_with_at
from pytwitchapi_helpers import is_valid_scrabble_tile
import json
import config
from remind_me import convert_time_hms_string_to_ms
from datetime import datetime, timedelta
from db import db_event_insert_one

APP_ID = os.environ['TWITCH_APP_ID']
APP_SECRET = os.environ['TWITCH_APP_SECRET']
# APP_ID = os.environ['TWITCH_APP_ID_LUNA']
# APP_SECRET = os.environ['TWITCH_APP_SECRET_LUNA']
USER_SCOPE = [
  # twitch
  AuthScope.MODERATOR_MANAGE_BANNED_USERS,
  # chat
  AuthScope.CHAT_READ,
  AuthScope.CHAT_EDIT,
  # pubsub
  AuthScope.CHANNEL_READ_REDEMPTIONS,
  AuthScope.BITS_READ,
  AuthScope.CHANNEL_READ_SUBSCRIPTIONS
]
TARGET_CHANNEL = 'smokie_777'

WHISPER_PREFIX_TEXT = '[respond to this message as if you were whispering. give a longer response than usual.]'
RANT_PREFIX_TEXT = '[please go on a really long and angry rant about the following topic.]'

async def pubsub_callback_listen_channel_points(uuid: UUID, data: dict) -> None:
  print('[PYTWITCHAPI]', data)
  title = data['data']['redemption']['reward']['title']
  display_name = data['data']['redemption']['user']['display_name']

  if title == 'luna whisper':
    vts_set_expression(VTS_EXPRESSIONS['FLUSHED'])
    user_input = data['data']['redemption']['user_input']
    prompt = f'{WHISPER_PREFIX_TEXT} {display_name}: {user_input}'
    with config.app.app_context():
      db_event_insert_one(
        type=TWITCH_EVENT_TYPE['CHANNEL_POINT_REDEMPTION'],
        event='luna whisper',
        body=user_input
      )
    config.priority_queue.enqueue(
      prompt=prompt,
      priority=PRIORITY_QUEUE_PRIORITIES['PRIORITY_PUBSUB_EVENTS_QUEUE'],
      azure_speaking_style=AZURE_SPEAKING_STYLE['WHISPERING']
    )
  elif title == 'luna rant':
    vts_set_expression(VTS_EXPRESSIONS['ANGRY'])
    user_input = data['data']['redemption']['user_input']
    prompt = f'{RANT_PREFIX_TEXT} {user_input}!'
    with config.app.app_context():
      db_event_insert_one(
        type=TWITCH_EVENT_TYPE['CHANNEL_POINT_REDEMPTION'],
        event='luna rant',
        body=user_input
      )
    config.priority_queue.enqueue(
      prompt=prompt,
      priority=PRIORITY_QUEUE_PRIORITIES['PRIORITY_PUBSUB_EVENTS_QUEUE']
    )
  elif title == 'Luna brown hair':
    with config.app.app_context():
      db_event_insert_one(
        type=TWITCH_EVENT_TYPE['CHANNEL_POINT_REDEMPTION'],
        event='Luna brown hair'
      )
    vts_set_expression(VTS_EXPRESSIONS['BROWN_HAIR'])
  elif title == 'smokie tts' and not config.is_singing:
    user_input = data['data']['redemption']['user_input']
    with config.app.app_context():
      db_event_insert_one(
        type=TWITCH_EVENT_TYPE['CHANNEL_POINT_REDEMPTION'],
        event='smokie tts',
        body=user_input
      )
    config.priority_queue.enqueue(
      prompt=user_input,
      priority=PRIORITY_QUEUE_PRIORITIES['PRIORITY_PUBSUB_EVENTS_QUEUE'],
      is_eleven_labs=True
    )

async def pubsub_callback_listen_bits_v1(uuid: UUID, data: dict) -> None:
  print('[PYTWITCHAPI]', data)
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
  config.priority_queue.enqueue(
    prompt=prompt, 
    priority=PRIORITY_QUEUE_PRIORITIES['PRIORITY_PUBSUB_EVENTS_QUEUE']
  )

async def pubsub_callback_listen_channel_subscriptions(uuid: UUID, data: dict) -> None:
  print('[PYTWITCHAPI]', data)
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
      ws_message = f'gift {multi_month_duration}-month {tier} sub --> {recipient_display_name}!'
      prompt = f'{ws_sub_name} just {ws_message}'
    else:
      ws_sub_name = display_name
      ws_message = f'gift {tier} sub --> {recipient_display_name}!'
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
  config.priority_queue.enqueue(
    prompt=prompt,
    priority=PRIORITY_QUEUE_PRIORITIES['PRIORITY_PUBSUB_EVENTS_QUEUE']
  )

async def chat_on_ready(ready_event: EventData):
  print('[PYTWITCHAPI] chat module connected')
  await ready_event.chat.join_room(TARGET_CHANNEL)

async def chat_on_message(msg: ChatMessage):
  # bits are handled in pubsub, so we ignore bit messages here
  if (
    msg.bits
    or WHISPER_PREFIX_TEXT in msg.text # channel point redemption will send a normal message too
    or RANT_PREFIX_TEXT in msg.text # channel point redemption will send a normal message too
  ):
    return

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
    if '@luna !remindme ' in msg.text.lower():
      args = msg.text.lower().replace('@luna !remindme ', '').split(' ')
      reminder_action = " ".join(args[1:])
      acknowledgement_prompt = (
        f'say, "I will remind {msg.user.name} to "{reminder_action}" in {args[0]}."'
      )
      reminder_prompt = f'say to {msg.user.name} that this is their reminder to "{reminder_action}".'
      config.remind_me_prompts_and_datetime_queue.append((
        reminder_prompt,
        datetime.now() + timedelta(milliseconds=convert_time_hms_string_to_ms(args[0]))
      ))
      with config.app.app_context():
        db_event_insert_one(
          type=TWITCH_EVENT_TYPE['CHAT_COMMAND'],
          event='!remindme',
          body=reminder_action
        )
      config.priority_queue.enqueue(
        prompt=acknowledgement_prompt,
        priority=PRIORITY_QUEUE_PRIORITIES['PRIORITY_REMIND_ME']
      )
    else:
      config.priority_queue.enqueue(
        prompt=prompt,
        priority=PRIORITY_QUEUE_PRIORITIES['PRIORITY_TWITCH_CHAT_QUEUE']
      )

async def chat_on_command_discord(cmd: ChatCommand):
  await cmd.reply('https://discord.gg/cxTHwepMTb 🖤✨')
  with config.app.app_context():
    db_event_insert_one(type=TWITCH_EVENT_TYPE['CHAT_COMMAND'], event='!discord')

async def chat_on_command_profile(cmd: ChatCommand):
  await cmd.reply('https://www.pathofexile.com/account/view-profile/smokie_777/characters 🖤✨')
  with config.app.app_context():
    db_event_insert_one(type=TWITCH_EVENT_TYPE['CHAT_COMMAND'], event='!profile')

async def chat_on_command_pob(cmd: ChatCommand):
  await cmd.reply('https://pobb.in/BgamVOOCQlH7 🖤✨')
  with config.app.app_context():
    db_event_insert_one(type=TWITCH_EVENT_TYPE['CHAT_COMMAND'], event='!pob')

async def chat_on_command_filter(cmd: ChatCommand):
  await cmd.reply('BASE FILTER (all gear hidden): https://www.filterblade.xyz/?profile=smokie_777&saveState=LVW1KYSNJXA3XV&platform=pc&isPreset=false\nLEAGUE START FILTER (base filter with semi-strict gear rules): https://www.filterblade.xyz/?profile=smokie_777&saveState=9VFGMVBQ4DK68P&platform=pc&isPreset=false\nBONESHATTER SLAYER FILTER (ILVL84+): https://www.filterblade.xyz/?profile=smokie_777&saveState=YV0J9GVYE6YON4&platform=pc&isPreset=false')
  with config.app.app_context():
    db_event_insert_one(type=TWITCH_EVENT_TYPE['CHAT_COMMAND'], event='!filter')

async def chat_on_command_video(cmd: ChatCommand):
  await cmd.reply('https://youtu.be/gTxQqJy3J3E 🖤✨')
  with config.app.app_context():
    db_event_insert_one(type=TWITCH_EVENT_TYPE['CHAT_COMMAND'], event='!video')

async def chat_on_command_build(cmd: ChatCommand):
  await cmd.reply('https://www.lastepochtools.com/planner/volrj1GQ 🖤✨')
  with config.app.app_context():
    db_event_insert_one(type=TWITCH_EVENT_TYPE['CHAT_COMMAND'], event='!build')

async def chat_on_command_play(cmd: ChatCommand):
  parameters = cmd.parameter.strip().lower().split(maxsplit=2)
  start_tile = parameters[0].strip() if len(parameters) > 0 else ''
  letters = parameters[1].strip() if len(parameters) > 1 else ''
  print('[SCRABBLE]', parameters, start_tile, letters)
  coordinate_str = start_tile[:-1] if start_tile[-1] in ['h', 'v'] else start_tile
  if (
    not letters.replace('_', '').isalpha()
    or not is_valid_scrabble_tile(coordinate_str)
  ):
    return
  config.ws.send(json.dumps({
    'scrabble_chat_command': {
      'type': 'play',
      'username': cmd.user.name,
      'letters': letters.upper(),
      # "start tile" refers to the leftmost/upmost tile of the primary word created.
      'startTileX': ord(coordinate_str[0]) - ord('a'), # already accounts for 0 index
      'startTileY': 14 - (int(coordinate_str[1:]) - 1), # subtract 1 to account for 0 index. invert for UI
      # default direction to 'horizontal'
      'direction': 'vertical' if start_tile[-1] == 'v' else 'horizontal'
    }
  }))

async def chat_on_command_ban(cmd: ChatCommand):
  if cmd.user.name == 'smokie_777':
    username_to_ban = cmd.text.replace('!ban ', '')
    if username_to_ban:
      prompt = f'Announce to everyone that {username_to_ban} has just been permanently banned from the channel! Feel free to add some spice :)'
      config.priority_queue.enqueue(
        prompt=prompt,
        priority=PRIORITY_QUEUE_PRIORITIES['PRIORITY_BAN_USER'],
        username_to_ban=username_to_ban
      )

async def terminate_pytwitchapi():
  config.chat.stop()
  config.pubsub.stop()
  await config.twitch.close()
    
async def run_pytwitchapi():
  config.twitch = await Twitch(APP_ID, APP_SECRET)
  auth = UserAuthenticator(config.twitch, USER_SCOPE, force_verify=False)
  token, refresh_token = await auth.authenticate()
  await config.twitch.set_user_authentication(token, USER_SCOPE, refresh_token)

  config.chat = await Chat(config.twitch)
  config.chat.register_event(ChatEvent.READY, chat_on_ready)
  config.chat.register_event(ChatEvent.MESSAGE, chat_on_message)
  config.chat.register_command('discord', chat_on_command_discord)
  config.chat.register_command('profile', chat_on_command_profile)
  config.chat.register_command('pob', chat_on_command_pob)
  config.chat.register_command('filter', chat_on_command_filter)
  config.chat.register_command('video', chat_on_command_video)
  config.chat.register_command('play', chat_on_command_play)
  config.chat.register_command('ban', chat_on_command_ban)
  config.chat.register_command('build', chat_on_command_build)
  config.chat.start()

  config.pubsub = PubSub(config.twitch)
  config.pubsub.start()
  await config.pubsub.listen_channel_points(
    str(os.environ['TWITCH_CHANNEL_ID']),
    pubsub_callback_listen_channel_points
  )
  await config.pubsub.listen_bits_v1(
    str(os.environ['TWITCH_CHANNEL_ID']),
    pubsub_callback_listen_bits_v1
  )
  await config.pubsub.listen_channel_subscriptions(
    str(os.environ['TWITCH_CHANNEL_ID']),
    pubsub_callback_listen_channel_subscriptions
  )
