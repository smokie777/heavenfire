from twitchAPI.helper import first
import config
import os
from dotenv import load_dotenv; load_dotenv()

async def ban_user_via_username(username, seconds = 60, reason = 'unknown reason'):
  print(f'attempting to ban the user called: {username} for {f"{seconds}s" if seconds is not None else "indefinitely"}')
  user_to_ban = await first(config.twitch.get_users(logins=[username.strip()]))
  if user_to_ban:
    await config.twitch.ban_user(
      os.environ['TWITCH_CHANNEL_ID'],
      os.environ['TWITCH_CHANNEL_ID'],
      user_to_ban.id,
      reason,
      seconds
    )
