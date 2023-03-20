from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from logging import basicConfig, INFO, info, error
from time import sleep
from os import listdir
from os.path import sep
from traceback import format_exc
from .helpers import userbots
from .helpers.telegram.groups import stream_end
from .translations import Translator

basicConfig(level=INFO)

name = __name__
bot_config = __import__(f'{__name__}.bot_config').bot_config
max_userbots = int(getattr(bot_config, 'MAX_ASSISTANT_COUNT', 4))
translator = Translator()
modules_dir = f"{__name__}{sep}modules"

'''
try:
    rmtree(f'{getcwd()}{sep}downloads', ignore_errors=True)
except:
    pass
'''

bot = Client(
    name,
    api_id=bot_config.API_ID,  # type: ignore
    api_hash=bot_config.API_HASH,  # type: ignore
    bot_token=bot_config.BOT_TOKEN,  # type: ignore
)

for module in sorted(listdir(modules_dir)):
    if module.endswith('.py') and module != '__init__.py':
        try:
            module_name = module.replace('.py', '')
            __import__(
                f"{modules_dir.replace(sep, '.')}.{module_name}")
            info(f'Module {module_name} imported!')
        except:
            error(f'An error occurred while import module {module}!')
            error(format_exc())


async def add_assistants():
    for i in range(1, max_userbots + 1):
        key = f'ASSISTANT_TOKEN{i}'
        if hasattr(bot_config, key) and getattr(bot_config, key):
            app = Client(
                f'{name}_user{i}',
                api_id=bot.api_id,  # type: ignore
                api_hash=bot.api_hash,
                session_string=getattr(bot_config, key),
            )
            calls = PyTgCalls(app)

            @calls.on_stream_end()
            async def stream_end_wrapper(client: PyTgCalls, update: Update):
                await stream_end(client, update)

            calls.start()
            userbots.append(calls)

            while not app.me:
                sleep(0.5)

            info(f'Loaded user: {app.me.first_name}, UID: {app.me.id}')

    if not len(userbots) and not getattr(bot_config, 'NO_USERBOT', False):
        error('No userbot instance found!')
        quit(1)

# execute async function without asyncio
routine = add_assistants()
try:
    routine.send(None)
except StopIteration:
    routine.close()
