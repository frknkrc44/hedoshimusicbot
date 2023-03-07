from typing import List
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import Update, StreamAudioEnded, StreamVideoEnded
from logging import basicConfig, INFO, info, error
from time import sleep
from os import listdir
from os.path import sep
from traceback import format_exc
from .helpers import userbots

basicConfig(level=INFO)

name = __name__
bot_config = __import__(f'{__name__}.bot_config').bot_config
max_userbots = int(getattr(bot_config, 'MAX_USERBOT_COUNT', 4))
translator = __import__('hedoshi.translations').translations.Translator()
modules_dir = f"{__name__}/modules"

bot = Client(
    name,
    api_id=bot_config.API_ID, # type: ignore
    api_hash=bot_config.API_HASH, # type: ignore
    bot_token=bot_config.BOT_TOKEN, # type: ignore
)

for module in listdir(modules_dir):
    if module.endswith('.py') and module != '__init__.py':
        try:
            __import__(f"{modules_dir.replace(sep, '.')}.{module.replace('.py', '')}")
            info(f'Module {module} imported!')
        except:
            error(f'An error occurred while import module {module}!')
            error(format_exc())

async def add_userbots():
    for i in range(1, max_userbots + 1):
        key = f'USERBOT_TOKEN{i}'
        if hasattr(bot_config, key) and getattr(bot_config, key):
            app = Client(
                f'{name}_user{i}',
                api_id=bot.api_id, # type: ignore
                api_hash=bot.api_hash,
                session_string=getattr(bot_config, key),
            )
            calls = PyTgCalls(app)
            
            @calls.on_stream_end()
            async def stream_end(client: PyTgCalls, update: Update):
                # if video stream ends, StreamAudioEnded and StreamVideoEnded is invoked
                # so we can ignore the video stream end signal
                if type(update) == StreamVideoEnded:
                    return

                try:
                    await client.leave_group_call(update.chat_id)
                except:
                    pass

                await bot.send_message(update.chat_id, text='Stream end')

            calls.start()
            userbots.append(calls)

            while not app.me:
                sleep(0.5)
            
            info(f'Loaded user: {app.me.first_name}, UID: {app.me.id}')

    if not len(userbots) and not getattr(bot_config, 'NO_USERBOT', False):
        error('No userbot instance found!')
        quit(1)

# execute async function without asyncio
routine = add_userbots()
try:
    routine.send(None)
except StopIteration:
    routine.close()
