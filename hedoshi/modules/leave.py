# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from pyrogram.types import Message

from ..translations import translator as _
from ..helpers.query import clear_query
from ..helpers.telegram.cmd_register import register
from ..helpers.telegram.groups import find_active_userbot
from ..helpers.telegram.msg_funcs import reply_message


@register(cmd="leave|ayril|end|son|bitir")
async def leave_call(message: Message):
    userbot = await find_active_userbot(message)
    if userbot:
        try:
            clear_query(message.chat.id)
            await userbot.leave_call(message.chat.id)
        except BaseException:
            pass

    await reply_message(
        message, text=_.translate_chat("streamEnd", cid=message.chat.id)
    )
