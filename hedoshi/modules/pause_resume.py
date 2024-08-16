# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from pyrogram.types import Message

from ..helpers.telegram.cmd_register import register
from ..helpers.telegram.groups import find_active_userbot
from ..helpers.telegram.msg_funcs import reply_message
from ..translations import translator as _


@register(cmd='resume|devam')
async def play(message: Message):
    userbot = await find_active_userbot(message)
    if userbot:
        try:
            await userbot.resume_stream(message.chat.id)
            await reply_message(
                message, _.translate_chat("streamResumed", cid=message.chat.id)
            )
        except BaseException:
            pass


@register(cmd='pause|duraklat')
async def pause(message: Message):
    userbot = await find_active_userbot(message)
    if userbot:
        try:
            await userbot.pause_stream(message.chat.id)
            await reply_message(
                message, _.translate_chat("streamPaused", cid=message.chat.id)
            )
        except BaseException:
            pass
