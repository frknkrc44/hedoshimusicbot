# Copyright (C) 2023 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from pyrogram.types import Message
from pytgcalls.types import StreamAudioEnded
from ..helpers.telegram.cmd_register import register
from ..helpers.telegram.groups import find_active_userbot, stream_end
from .. import translator as _


@register(cmd='skip|next|sonraki')
async def skip(message: Message):
    userbot = await find_active_userbot(message)
    if userbot:
        try:
            await userbot.get_active_call(message.chat.id)
            await stream_end(userbot, update=StreamAudioEnded(message.chat.id), force_skip=True)
            return
        except:
            pass

    await message.reply(_.translate_chat('queryEmpty', cid=message.chat.id))
