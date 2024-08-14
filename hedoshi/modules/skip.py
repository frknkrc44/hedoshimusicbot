# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from pyrogram.types import Message
from pytgcalls.types import StreamAudioEnded

from .. import translator as _
from ..helpers.telegram.cmd_register import register
from ..helpers.telegram.groups import (find_active_userbot, is_active,
                                       stream_end)
from ..helpers.telegram.msg_funcs import reply_message


@register(cmd='skip|next|sonraki')
async def skip(message: Message):
    userbot = await find_active_userbot(message)
    if userbot:
        try:
            assert await is_active(message.chat.id, userbot)
            await stream_end(userbot, update=StreamAudioEnded(message.chat.id), force_skip=True)
            return
        except BaseException:
            pass

    await reply_message(message, _.translate_chat("queryEmpty", cid=message.chat.id))
