import discord
import os
from gen_llm_response import gen_llm_response
import random
import datetime
from log_error import log_error
import asyncio
from datetime import timedelta
from tts import gen_audio_file_and_subtitles
from dotenv import load_dotenv; load_dotenv()

def get_current_minute():
  current_time = datetime.datetime.now()
  return current_time.minute

def get_current_hour():
  current_time = datetime.datetime.now()
  return current_time.hour

current_minute = get_current_minute()
current_hour = get_current_hour()

MAX_MESSAGES_PER_MINUTE = 5
MAX_MESSAGES_PER_HOUR = 15
MAX_MESSAGES_PER_SESSION = 50

messages_per_minute_counter = 0
messages_per_hour_counter = 0

is_luna_busy = False

vc = None

client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  global current_minute
  global current_hour
  global messages_per_minute_counter
  global messages_per_hour_counter
  global is_luna_busy
  global vc

  # don't respond to itself, or if currently working through a response.
  if message.author == client.user or is_luna_busy:
    return

  is_luna_busy = True

  # only respond to messages if BOTH message is from Alluring Lunar Haven AND @LUnA was mentioned
  if str(message.guild) == 'Alluring Lunar Haven':
    if int(os.environ['LUNA_DISCORD_BOT_ID']) in [m.id for m in message.mentions]:
      # print('message.activity: ', message.activity)
      # print('message.application: ', message.application)
      # print('message.application_id: ', message.application_id)
      # print('message.attachments: ', message.attachments)
      # print('message.author: ', message.author)
      # print('message.channel: ', message.channel)
      # print('message.channel_mentions: ', message.channel_mentions)
      # print('message.clean_content: ', message.clean_content)
      # print('message.components: ', message.components)
      # print('message.content: ', message.content)
      # print('message.created_at: ', message.created_at)
      # print('message.edited_at: ', message.edited_at)
      # print('message.embeds: ', message.embeds)
      # print('message.flags: ', message.flags)
      # print('message.guild: ', message.guild)
      # print('message.id: ', message.id)
      # print('message.interaction: ', message.interaction) 
      # print('message.jump_url: ', message.jump_url)
      # print('message.mention_everyone: ', message.mention_everyone)
      # print('message.mentions: ', message.mentions)
      # print('message.nonce: ', message.nonce)
      # print('message.pinned: ', message.pinned)
      # print('message.position: ', message.position)
      # print('message.raw_channel_mentions: ', message.raw_channel_mentions)
      # print('message.raw_mentions: ', message.raw_mentions)
      # print('message.raw_role_mentions: ', message.raw_role_mentions)
      # print('message.reactions: ', message.reactions)
      # print('message.reference: ', message.reference)
      # print('message.role_mentions: ', message.role_mentions)
      # print('message.role_subscription: ', message.role_subscription)
      # print('message.stickers: ', message.stickers)
      # print('message.system_content: ', message.system_content)
      # print('message.tts: ', message.tts)
      # print('message.type: ', message.type)
      # print('message.webhook_id: ', message.webhook_id)

      # rate limiting logic (per minute and hour)
      updated_current_minute = get_current_minute()
      updated_current_hour = get_current_hour()
      
      if (current_minute != updated_current_minute):
        messages_per_minute_counter = 0
        current_minute = updated_current_minute
      if (current_hour != updated_current_hour):
        messages_per_hour_counter = 0
        current_hour = updated_current_hour

      if (messages_per_minute_counter < MAX_MESSAGES_PER_MINUTE and messages_per_hour_counter < MAX_MESSAGES_PER_HOUR):
        try:
          prompt = ''

          # ban functionality
          if (str(message.author) == 'smokie_777' and '@LUnA ban' in str(message.clean_content)):
            await message.mentions[1].ban()
            (_, _, edited) = gen_llm_response('Smokie: luna, announce that you\'ve just banned ' + message.mentions[1].display_name + ' out of your discord server. feel free to include some spice :)')
            async with message.channel.typing():
              await asyncio.sleep(random.uniform(2, 4))
            await message.reply(edited)
          # timeout functionality
          elif (str(message.author) == 'smokie_777' and '@LUnA timeout' in str(message.clean_content)):
            delta = timedelta(days=0, seconds=777, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
            await message.mentions[1].timeout(delta)
            (_, _, edited) = gen_llm_response('Smokie: luna, announce that you\'ve just timed out ' + message.mentions[1].display_name + ' for 777 seconds. feel free to include some spice :)')
            async with message.channel.typing():
              await asyncio.sleep(random.uniform(2, 4))
            await message.reply(edited)
          # remote shut down functionality
          elif (str(message.author) == 'smokie_777' and '@LUnA sleep' in str(message.clean_content)):
            await client.close()
          # bot join voice channel
          elif (str(message.author) == 'smokie_777' and '@LUnA vc' in str(message.clean_content)):
            channel = message.author.voice.channel
            # channel = message.guild.get_channel(1139810743471063053)
            if vc is not None:
              await vc.disconnect()
              vc = None
            else:
              vc = await channel.connect()
          # general message response function
          else:
            messages_per_minute_counter += 1
            messages_per_hour_counter += 1
            prompt = str(message.author.display_name) + ': ' + str(message.clean_content)
            (_, _, edited) = gen_llm_response(prompt)

            if vc is not None and (message.channel.name == 'voice-text' or message.channel.name == 'luna-and-smokie-only'):
              await message.reply(edited)
              (filename, _) = gen_audio_file_and_subtitles(edited, None, True)
              try:
                # todo: in collab mode, do a post request to the flask server
                vc.play(discord.FFmpegPCMAudio(filename))
              except:
                print('skipping')
            else:
              async with message.channel.typing():
                await asyncio.sleep(random.uniform(2, 4))
              await message.reply(edited)

        except Exception as e:
          log_error(e, '(discord bot)')
          await message.reply('Someone tell @smokie_777 there is a problem with my AI.')
      else:
        await message.reply('⌛')
    # luna bot respond to transcription
    elif (
      message.channel.name == 'transcription'
      and str(message.author) == 'SeaVoice#8208'
      and vc is not None
      and len(str(message.clean_content).split(':  ')[-1].split()) > 1
      and str(message.clean_content).split(':  ')[0] != '**LUnA**'
    ):
      prompt = str(message.clean_content.replace('*', ''))
      (_, _, edited) = gen_llm_response(prompt)
      (filename, _) = gen_audio_file_and_subtitles(edited, None, True)
      try:
        vc.play(discord.FFmpegPCMAudio(filename))
      except:
        print('skipping')

  is_luna_busy = False


if __name__ == '__main__':
  client.run(os.environ['LUNA_DISCORD_BOT_TOKEN'])
