# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from pyrogram.types import Message
from pytgcalls.types import MediaStream
from ..helpers.telegram.cmd_register import register
from ..helpers.query import get_next_query, replace_query, QueryItem
from ..helpers.telegram.groups import find_active_userbot, join_or_change_stream
from .. import translator as _


@register(cmd='seek|ileriatla')
async def seek(message: Message):
    await _seek(message, False)


@register(cmd='seekback|geriatla')
async def sback(message: Message):
    await _seek(message, True)


@register(cmd='seekstart|basaatla')
async def fback(message: Message):
    message.command.insert(1, '99999999')
    await _seek(message, True)


async def _seek(message: Message, back_mode: bool):
    userbot = await find_active_userbot(message)
    if userbot:
        try:
            seconds = int(message.command[1])
            assert seconds > 0
        except BaseException:
            return

        item = get_next_query(message.chat.id)
        if not item:
            return

        msg = await message.reply(_.translate_chat(
            'streamBackSeeking' if back_mode else 'streamSeeking', cid=item.chat_id))
        played = await userbot.played_time(item.chat_id)

        if back_mode:
            skip = item.skip - (played + seconds)
            if skip < 0:
                skip = 0
        else:
            skip = item.skip + played + seconds
            if skip >= item.duration:
                skip = item.duration

        piped = MediaStream(
            item.stream._media_path,
            video_flags=MediaStream.Flags.IGNORE
            if not item.video
            else MediaStream.Flags.AUTO_DETECT,
            ffmpeg_parameters=f"-ss {skip}",
            video_parameters=item.stream._video_parameters,
        )

        replace_query(
            item,
            QueryItem(piped, item.duration, skip, item.chat_id, item.loop, item.video),
        )
        await join_or_change_stream(
            message=msg,
            stream=piped,
            action=1,
        )
        await msg.edit(_.translate_chat(
            'streamBackSeeked' if back_mode else 'streamSeeked', cid=item.chat_id))
