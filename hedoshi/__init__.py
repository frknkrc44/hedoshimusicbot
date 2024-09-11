# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from asyncio import iscoroutine, run
from asyncio import sleep as async_sleep
from logging import (FATAL, INFO, LogRecord, NullHandler, basicConfig, error,
                     getLogger, info)
from os import listdir, mkdir, remove
from os.path import exists, isfile, sep
from time import sleep
from traceback import format_exc
from typing import Callable

from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls import filters as CallFilters
from pytgcalls.types import ChatUpdate

from .helpers import userbots

basicConfig(level=INFO)
getLogger("httpx").setLevel(FATAL)

class MyNullHandler(NullHandler):
    def __init__(
        self,
        level: int | str = INFO,
        signal_text: str = "Connection lost",
        on_trigger: Callable[[], None] = None,
    ) -> None:
        super().__init__(level)
        self.signal_text = signal_text
        self.on_trigger = on_trigger

    def handle(self, record: LogRecord) -> bool:
        if self.signal_text in record.getMessage():
            if iscoroutine(self.on_trigger):
                run(self.on_trigger())
            else:
                self.on_trigger()

        return super().handle(record)


name = __name__
bot_config = __import__(f"{__name__}.bot_config").bot_config
max_userbots = int(getattr(bot_config, "MAX_ASSISTANT_COUNT", 4))
modules_dir = f"{__name__}{sep}modules"

if not exists("downloads"):
    mkdir("downloads")
else:
    remove_file_enabled = (
        bot_config.BOT_REMOVE_FILE_AUTO
        if hasattr(bot_config, "BOT_REMOVE_FILE_AUTO")
        else False
    )

    if remove_file_enabled:
        for item in listdir("downloads"):
            item = f"downloads/{item}"
            if isfile(item):
                remove(item)


def reconnect(client: Client):
    async def fn():
        try:
            await client.disconnect()
        except BaseException:
            pass

        await async_sleep(2)

        try:
            await client.connect()
        except BaseException:
            pass

    return fn


def force_quit():
    quit()


bot = Client(
    name,
    api_id=bot_config.API_ID,  # type: ignore
    api_hash=bot_config.API_HASH,  # type: ignore
    bot_token=bot_config.BOT_TOKEN,  # type: ignore
)

getLogger("pyrogram.connection.transport.tcp.tcp").addHandler(
    MyNullHandler(
        on_trigger=reconnect(bot),
    )
)

# Force quit
getLogger("root").addHandler(
    MyNullHandler(
        signal_text="Stop signal received",
        on_trigger=force_quit,
    )
)

for module in sorted(listdir(modules_dir)):
    if module.endswith('.py') and module != '__init__.py':
        try:
            module_name = module.replace('.py', '')
            __import__(
                f"{modules_dir.replace(sep, '.')}.{module_name}")
            info(f'Module {module_name} imported!')
        except BaseException:
            error(f"An error occurred while import module {module}!")
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

            getLogger("pyrogram.connection.transport.tcp.tcp").addHandler(
                MyNullHandler(
                    on_trigger=reconnect(app),
                )
            )
            calls = PyTgCalls(app)

            from .helpers.telegram.groups import stream_end, vc_closed

            calls.add_handler(CallFilters.stream_end, stream_end)
            calls.add_handler(
                CallFilters.chat_update(ChatUpdate.Status.CLOSED_VOICE_CHAT),
                vc_closed,
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
