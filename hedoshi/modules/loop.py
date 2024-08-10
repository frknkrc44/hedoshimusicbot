# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from ..helpers.query import get_next_query
from ..helpers.telegram.cmd_register import register
from pyrogram.types import Message
from .. import translator as _


@register(cmd='loop|dongu|döngü')
async def set_loop(message: Message):
    item = get_next_query(message.chat.id)
    if not item:
        await message.reply(_.translate_chat('queryEmpty', cid=message.chat.id))
        return

    if not item.loop:
        item.loop = True
        await message.reply(_.translate_chat('loopOn', cid=message.chat.id))
    else:
        item.loop = False
        await message.reply(_.translate_chat('loopOff', cid=message.chat.id))
