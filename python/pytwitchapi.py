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
from pytwitchapi_helpers import is_valid_scrabble_tile, send_ban_user_via_username_event_to_priority_queue, is_twitch_message_bot_spam, find_banned_words
import json
from remind_me import convert_time_hms_string_to_ms
from datetime import datetime, timedelta
from db import db_event_insert_one
from InstanceContainer import InstanceContainer
from State import State

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

  if title == 'luna whisper' and State.is_twitch_chat_react_on:
    vts_set_expression(VTS_EXPRESSIONS['FLUSHED'])
    user_input = data['data']['redemption']['user_input']
    prompt = f'{WHISPER_PREFIX_TEXT} {display_name}: {user_input}'
    with InstanceContainer.app.app_context():
      db_event_insert_one(
        type=TWITCH_EVENT_TYPE['CHANNEL_POINT_REDEMPTION'],
        event='luna whisper',
        body=user_input
      )
    InstanceContainer.priority_queue.enqueue(
      prompt=prompt,
      priority=PRIORITY_QUEUE_PRIORITIES['PRIORITY_PUBSUB_EVENTS_QUEUE'],
      azure_speaking_style=AZURE_SPEAKING_STYLE['WHISPERING']
    )
  elif title == 'luna rant' and State.is_twitch_chat_react_on:
    vts_set_expression(VTS_EXPRESSIONS['ANGRY'])
    user_input = data['data']['redemption']['user_input']
    prompt = f'{RANT_PREFIX_TEXT} {user_input}!'
    with InstanceContainer.app.app_context():
      db_event_insert_one(
        type=TWITCH_EVENT_TYPE['CHANNEL_POINT_REDEMPTION'],
        event='luna rant',
        body=user_input
      )
    InstanceContainer.priority_queue.enqueue(
      prompt=prompt,
      priority=PRIORITY_QUEUE_PRIORITIES['PRIORITY_PUBSUB_EVENTS_QUEUE']
    )
  elif title == 'Luna brown hair':
    with InstanceContainer.app.app_context():
      db_event_insert_one(
        type=TWITCH_EVENT_TYPE['CHANNEL_POINT_REDEMPTION'],
        event='Luna brown hair'
      )
    vts_set_expression(VTS_EXPRESSIONS['BROWN_HAIR'])
  elif title == 'smokie tts' and not State.is_singing:
    user_input = data['data']['redemption']['user_input']
    with InstanceContainer.app.app_context():
      db_event_insert_one(
        type=TWITCH_EVENT_TYPE['CHANNEL_POINT_REDEMPTION'],
        event='smokie tts',
        body=user_input
      )
    InstanceContainer.priority_queue.enqueue(
      prompt=user_input,
      priority=PRIORITY_QUEUE_PRIORITIES['PRIORITY_PUBSUB_EVENTS_QUEUE'],
      is_eleven_labs=True
    )
  elif title == 'unlock 7tv emote':
    user_input = data['data']['redemption']['user_input']
    prompt = f'{display_name} just requested adding the {user_input} 7tv emote!'
    with InstanceContainer.app.app_context():
      db_event_insert_one(
        type=TWITCH_EVENT_TYPE['CHANNEL_POINT_REDEMPTION'],
        event='unlock 7tv emote',
        body=user_input
      )
    InstanceContainer.priority_queue.enqueue(
      prompt=prompt,
      priority=PRIORITY_QUEUE_PRIORITIES['PRIORITY_PUBSUB_EVENTS_QUEUE']
    )

async def pubsub_callback_listen_bits_v1(uuid: UUID, data: dict) -> None:
  print('[PYTWITCHAPI]', data)
  data = data.get('data')
  user_name = data.get('user_name')
  bits = data.get('bits_used')
  chat_message = data.get('chat_message')
  prompt = f'{user_name} just cheered {bits} bits! Their message: {chat_message}'
  # send bits data to websocket
  InstanceContainer.ws.send(json.dumps({
    'twitch_event': {
      'event': TWITCH_EVENTS['BITS'],
      'username': user_name,
      'value': str(bits)
    }
  }))
  InstanceContainer.priority_queue.enqueue(
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
  InstanceContainer.ws.send(json.dumps({
    'twitch_event': {
      'event': TWITCH_EVENTS['SUB'],
      'username': ws_sub_name,
      'value': ws_message
    }
  }))
  InstanceContainer.priority_queue.enqueue(
    prompt=prompt,
    priority=PRIORITY_QUEUE_PRIORITIES['PRIORITY_PUBSUB_EVENTS_QUEUE']
  )

async def chat_on_ready(ready_event: EventData):
  print('[PYTWITCHAPI] chat module connected')
  await ready_event.chat.join_room(TARGET_CHANNEL)

async def chat_on_message(msg: ChatMessage):
  # print(msg.__dict__)

  if (
    msg._parsed['tags']['first-msg'] == '1'
    and is_twitch_message_bot_spam(msg.text)
  ):
    print(f'[PYTWITCHAPI] {msg.user.name} was detected as a spam bot, is about to be banned! Their message: {msg.text}')
    send_ban_user_via_username_event_to_priority_queue(
      msg.user.name,
      None,
      'being a spam bot'
    )
    return
  
  banned_words_in_message = find_banned_words(msg.text)
  if len(banned_words_in_message):
    print(f'[PYTWITCHAPI] {msg.user.name} said a banned word, is about to be timed out! Their message: {msg.text}')
    send_ban_user_via_username_event_to_priority_queue(
      msg.user.name,
      10,
      f'saying a banned word in chat: {banned_words_in_message[0]} (mention the banned word in your response!)'
    )
    return

  # bits are handled in pubsub, so we ignore bit messages here
  if (
    msg.bits
    or WHISPER_PREFIX_TEXT in msg.text # channel point redemption will send a normal message too
    or RANT_PREFIX_TEXT in msg.text # channel point redemption will send a normal message too
  ):
    return
  
  InstanceContainer.ws.send(json.dumps({
    'twitch_event': {
      'event': TWITCH_EVENTS['MESSAGE'],
      'username': msg.user.name,
      'value': msg.text
    }
  }))

  prompt = f'{msg.user.name}: {msg.text}'
  is_at_luna = '@luna' in msg.text.lower() or '@hellfire' in msg.text.lower()

  if (
    State.is_twitch_chat_react_on
    and msg.text[0] != '!'
    and msg.user.name != 'Streamlabs'
    and (
      (State.is_quiet_mode_on and is_at_luna)
      or (not State.is_quiet_mode_on and (
        is_at_luna or not does_one_word_start_with_at(msg.text.lower().split(' '))
      ))
    )
  ):
    if '@luna !remindme ' in msg.text.lower():
      args = msg.text.lower().replace('@luna !remindme ', '').split(' ')
      reminder_action = " ".join(args[1:])
      acknowledgement_prompt = (
        f'say, "I will remind {msg.user.name} to "{reminder_action}" in {args[0]}."'
      )
      reminder_prompt = f'say to {msg.user.name} that this is their reminder to "{reminder_action}".'
      State.remind_me_prompts_and_datetime_queue.append((
        reminder_prompt,
        datetime.now() + timedelta(milliseconds=convert_time_hms_string_to_ms(args[0]))
      ))
      with InstanceContainer.app.app_context():
        db_event_insert_one(
          type=TWITCH_EVENT_TYPE['CHAT_COMMAND'],
          event='!remindme',
          body=reminder_action
        )
      InstanceContainer.priority_queue.enqueue(
        prompt=acknowledgement_prompt,
        priority=PRIORITY_QUEUE_PRIORITIES['PRIORITY_REMIND_ME']
      )
    else:
      InstanceContainer.priority_queue.enqueue(
        prompt=prompt,
        priority=PRIORITY_QUEUE_PRIORITIES['PRIORITY_TWITCH_CHAT_QUEUE']
      )

async def chat_on_command_discord(cmd: ChatCommand):
  await cmd.reply('https://discord.gg/cxTHwepMTb')
  with InstanceContainer.app.app_context():
    db_event_insert_one(type=TWITCH_EVENT_TYPE['CHAT_COMMAND'], event='!discord')

async def chat_on_command_profile(cmd: ChatCommand):
  await cmd.reply('https://www.pathofexile.com/account/view-profile/smokie_777/characters')
  with InstanceContainer.app.app_context():
    db_event_insert_one(type=TWITCH_EVENT_TYPE['CHAT_COMMAND'], event='!profile')

async def chat_on_command_filter(cmd: ChatCommand):
  await cmd.reply('https://www.filterblade.xyz/Profile?name=smokie_777&platform=pc')
  # await cmd.reply('https://pastebin.com/XRCCuqhK')
  with InstanceContainer.app.app_context():
    db_event_insert_one(type=TWITCH_EVENT_TYPE['CHAT_COMMAND'], event='!filter')

async def chat_on_command_video(cmd: ChatCommand):
  await cmd.reply('https://www.youtube.com/@smokie_777')
  with InstanceContainer.app.app_context():
    db_event_insert_one(type=TWITCH_EVENT_TYPE['CHAT_COMMAND'], event='!video')

async def chat_on_command_build(cmd: ChatCommand):
  await cmd.reply('https://poe.ninja/pob/5d214')
  with InstanceContainer.app.app_context():
    db_event_insert_one(type=TWITCH_EVENT_TYPE['CHAT_COMMAND'], event='!build')

async def chat_on_command_rip(cmd: ChatCommand):
  await cmd.reply('https://clips.twitch.tv/SpotlessImportantTigerNotATK-y8BriY_NBlNwA8a5')
  with InstanceContainer.app.app_context():
    db_event_insert_one(type=TWITCH_EVENT_TYPE['CHAT_COMMAND'], event='!rip')

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
  InstanceContainer.ws.send(json.dumps({
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
    args = cmd.text.replace('!ban ', '').split(' ')
    username_to_ban = args[0].strip()
    reason = ''
    if len(args) > 1:
      reason = args[1].strip()
    if username_to_ban:
      send_ban_user_via_username_event_to_priority_queue(username_to_ban, None, reason)

async def terminate_pytwitchapi():
  InstanceContainer.chat.stop()
  InstanceContainer.pubsub.stop()
  await InstanceContainer.twitch.close()
    
async def run_pytwitchapi():
  InstanceContainer.twitch = await Twitch(APP_ID, APP_SECRET)
  auth = UserAuthenticator(InstanceContainer.twitch, USER_SCOPE, force_verify=False)
  token, refresh_token = await auth.authenticate()
  await InstanceContainer.twitch.set_user_authentication(token, USER_SCOPE, refresh_token)

  InstanceContainer.chat = await Chat(InstanceContainer.twitch)
  InstanceContainer.chat.register_event(ChatEvent.READY, chat_on_ready)
  InstanceContainer.chat.register_event(ChatEvent.MESSAGE, chat_on_message)
  InstanceContainer.chat.register_command('discord', chat_on_command_discord)
  InstanceContainer.chat.register_command('profile', chat_on_command_profile)
  InstanceContainer.chat.register_command('filter', chat_on_command_filter)
  InstanceContainer.chat.register_command('video', chat_on_command_video)
  InstanceContainer.chat.register_command('play', chat_on_command_play)
  InstanceContainer.chat.register_command('ban', chat_on_command_ban)
  InstanceContainer.chat.register_command('rip', chat_on_command_rip)
  InstanceContainer.chat.register_command('build', chat_on_command_build)
  InstanceContainer.chat.register_command('pob', chat_on_command_build)
  InstanceContainer.chat.start()

  InstanceContainer.pubsub = PubSub(InstanceContainer.twitch)
  InstanceContainer.pubsub.start()
  await InstanceContainer.pubsub.listen_channel_points(
    str(os.environ['TWITCH_CHANNEL_ID']),
    pubsub_callback_listen_channel_points
  )
  await InstanceContainer.pubsub.listen_bits_v1(
    str(os.environ['TWITCH_CHANNEL_ID']),
    pubsub_callback_listen_bits_v1
  )
  await InstanceContainer.pubsub.listen_channel_subscriptions(
    str(os.environ['TWITCH_CHANNEL_ID']),
    pubsub_callback_listen_channel_subscriptions
  )
