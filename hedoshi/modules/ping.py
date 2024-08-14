# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from time import time

from pyrogram.types import Message

from ..helpers.telegram.cmd_register import register
from ..helpers.telegram.msg_funcs import edit_message, reply_message


@register('ping|check|denetle', private=True)
async def ping(message: Message) -> None:
    start = time()
    msg = await reply_message(message, "Pong!")
    delta = time() - start
    await edit_message(msg, f"Pong! - {delta*1000:.0f}ms")
