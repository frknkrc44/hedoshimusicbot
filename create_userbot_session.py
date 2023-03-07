from pyrogram import Client
from dotenv import dotenv_values

values = dotenv_values('config.env')

userbot = Client(
    ':memory:',
    api_id=values['API_ID'],
    api_hash=values['API_HASH'],
)

with userbot:
    print(userbot.export_session_string())
