# Copyright (C) 2020-2023 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from pyrogram.types import Message
from ..helpers.telegram.cmd_register import register
from time import time


@register('ping|check|denetle', private=True)
async def ping(message: Message) -> None:
    start = time()
    msg = await message.reply_text('Pong!')
    delta = time() - start
    await msg.edit(f'Pong! - {delta*1000:.0f}ms')
