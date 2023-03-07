from pyrogram import Client
from dotenv import dotenv_values

values = dotenv_values('config.env')

userbot = Client(
    ':memory:',
    api_id=values['API_ID'],  # type: ignore
    api_hash=values['API_HASH'],  # type: ignore
    in_memory=bool(values.get('CREATE_SESSION_MEMORY', False)),
)

with userbot:
    print(userbot.export_session_string())
