# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from pyrogram.types import Message

from ..helpers.query import get_next_query
from ..helpers.telegram.cmd_register import register
from ..helpers.telegram.msg_funcs import reply_message
from ..translations import translator as _


@register(cmd='loop|dongu|döngü')
async def set_loop(message: Message):
    item = get_next_query(message.chat.id)
    if not item:
        await reply_message(
            message, _.translate_chat("queryEmpty", cid=message.chat.id)
        )
        return

    if not item.loop:
        item.loop = True
        await reply_message(message, _.translate_chat("loopOn", cid=message.chat.id))
    else:
        item.loop = False
        await reply_message(message, _.translate_chat("loopOff", cid=message.chat.id))
