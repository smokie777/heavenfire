import sys; sys.path.append('../server')
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
from twitchAPI.pubsub import PubSub
from uuid import UUID
import asyncio
import os
import config
from time import sleep
from execute_action import execute_or_enqueue_action
from dotenv import load_dotenv; load_dotenv()

twitch = None
chat = None
pubsub = None

APP_ID = os.environ['TWITCH_APP_ID']
APP_SECRET = os.environ['TWITCH_APP_SECRET']
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
  True

async def pubsub_callback_listen_bits_v1(uuid: UUID, data: dict) -> None:
  user_name = data.get('user_name')
  bits = data.get('bits_used')
  chat_message = data.get('chat_message')
  prompt = f'{user_name} just cheered {bits} bits! Their message: {chat_message}'
  execute_or_enqueue_action((prompt, 1))

async def pubsub_callback_listen_channel_subscriptions(uuid: UUID, data: dict) -> None:
  prompt = ''
  display_name = data.get('display_name')
  tier = '"Prime"' if data.get('sub_plan') == 'Prime' else str((int(data.get('sub_plan')) // 1000))
  is_gift = data.get('is_gift')
  recipient_display_name = data.get('recipient_display_name')
  multi_month_duration = data.get('multi_month_duration')
  cumulative_months = data.get('cumulative_months')
  if is_gift:
    gifter_name = display_name if display_name else 'An anonymous gifter'
    if multi_month_duration:
      prompt = f'{gifter_name} just gifted a {multi_month_duration}-month tier {tier} sub to {recipient_display_name}'
    else:
        prompt = f'{gifter_name} just gifted a tier {tier} sub to {recipient_display_name}'
  else:
    if multi_month_duration:
      prompt = f'{display_name} just bought a {multi_month_duration}-month tier {tier} sub'
    elif cumulative_months > 1:
      prompt = f'{display_name} just subscribed for {cumulative_months} months!'
    else:
      prompt = f'{display_name} just subscribed' if tier == 1 else f'{display_name} just subscribed at tier {tier}'
  prompt = prompt.replace('tier 1 sub', 'sub')
  execute_or_enqueue_action((prompt, 1))

async def chat_on_ready(ready_event: EventData):
  print('pytwitchapi chat connected')
  await ready_event.chat.join_room(TARGET_CHANNEL)

async def chat_on_message(msg: ChatMessage):
  prompt = f'{msg.user.name}: {msg.text}'
  execute_or_enqueue_action((prompt, 5))

async def chat_on_command_discord(cmd: ChatCommand):
  await cmd.reply('https://discord.gg/cxTHwepMTb')

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
  asyncio.run(run_pytwitchapi())
  