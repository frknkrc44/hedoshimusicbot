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
from ..helpers.telegram.downloader import (download_and_start_tg_media, start_stream,
                                           parse_telegram_url, parse_telegram_url_and_stream)
from ..helpers.youtube import ytdl_wrapper as youtube, yt_search
from .. import translator as _


@register(cmd='play|oynat|baslat|vplay|voynat|vbaslat')
async def play(message: Message):
    msg = await message.reply_text(_.translate_chat('mvProcessing', cid=message.chat.id))
    video_mode = message.command[0].startswith('v')

    if message.reply_to_message:
        reply = message.reply_to_message
        is_audio = reply.audio is not None or reply.voice is not None or (
            reply.document and 'audio' in reply.document.mime_type)
        is_video = reply.video is not None or (
            reply.document and 'video' in reply.document.mime_type)

        if is_audio or is_video:
            await download_and_start_tg_media(msg, reply, is_video=(video_mode and is_video))
            return
    else:
        if len(message.command) > 1:
            command = ' '.join(message.command[1:])
            if parse_telegram_url(command)[0]:  # type: ignore
                return await parse_telegram_url_and_stream(msg, command, video_mode)
            elif youtube.is_valid(command):
                path = youtube.download_media(
                    command, msg, not video_mode)
                if path:
                    await start_stream(msg, path, video_mode)
                    return
            else:
                if search := yt_search.search_query(command):
                    if youtube.is_valid(search):  # type: ignore
                        path = youtube.download_media(
                            search, msg, not video_mode)  # type: ignore
                        if path:
                            await start_stream(msg, path, video_mode)
                            return

    await msg.edit(_.translate_chat('streamNoSrc', cid=message.chat.id))
