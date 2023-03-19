from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import Update, StreamAudioEnded, AudioPiped, AudioVideoPiped, HighQualityAudio, HighQualityVideo
from logging import basicConfig, INFO, info, error
from time import sleep
from os import listdir, getcwd
from shutil import rmtree
from os.path import sep
from traceback import format_exc
from .helpers.telegram.groups import join_or_change_stream
from .helpers import userbots, get_next_query, query
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
            async def stream_end(client: PyTgCalls, update: Update):
                # if video stream ends, StreamAudioEnded and StreamVideoEnded is invoked
                # so we can ignore the video stream end signal
                if type(update) != StreamAudioEnded:
                    return

                item = get_next_query(update.chat_id, True)
                print(item)
                if item and item.loop:
                    if type(item.stream) == AudioPiped:
                        piped = AudioPiped(
                            path=item.stream._path,
                            audio_parameters=HighQualityAudio(),
                        )
                    else:
                        piped = AudioVideoPiped(
                            path=item.stream._path,
                            audio_parameters=HighQualityAudio(),
                            video_parameters=HighQualityVideo(),
                        )

                    item.stream = piped
                    item.skip = 0
                    query.insert(0, item)

                item = get_next_query(update.chat_id)
                if item:
                    msg = await bot.send_message(
                        update.chat_id,
                        text=translator.translate_chat(
                            'streamNext' if not item.loop else 'streamLoop',
                            cid=update.chat_id,
                        )
                    )
                    await join_or_change_stream(msg, item.stream, 1)
                    return

                try:
                    await client.leave_group_call(update.chat_id)
                except:
                    pass

                await bot.send_message(
                    update.chat_id,
                    text=translator.translate_chat(
                        'streamEnd', cid=update.chat_id)
                )

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
