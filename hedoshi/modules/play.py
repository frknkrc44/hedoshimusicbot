# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from os.path import basename
from pyrogram.types import Message
from ..helpers.telegram.cmd_register import register
from ..helpers.telegram.downloader import (download_and_start_tg_media, start_stream,
                                           parse_telegram_url, parse_telegram_url_and_stream)
from ..helpers.telegram.groups import find_active_userbot, add_userbot
from ..helpers.youtube import ytdl_wrapper as youtube, yt_search
from ..helpers.spotify import is_spotify_track
from .. import translator as _


@register(
    cmd="play|oynat|baslat|vplay|voynat|vbaslat",
    bot_admin=True,
)
async def play(message: Message):
    msg = await message.reply_text(_.translate_chat('mvProcessing', cid=message.chat.id))
    video_mode = message.command[0].startswith('v')

    calls = await find_active_userbot(message)
    if not calls:
        await msg.edit(_.translate_chat("astJoining", cid=message.chat.id))
        try:
            added = await add_userbot(message)
            assert added
        except BaseException:
            await msg.edit(_.translate_chat("astJoinFail", cid=message.chat.id))
            return

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
            elif youtube.is_valid(command) and not is_spotify_track(command):
                path = await youtube.download_media(command, not video_mode)
                if path:
                    await start_stream(msg, path, video_mode, basename(path))
                    return
            else:
                if is_spotify_track(command):
                    search = await yt_search.search_from_spotify_link(command)
                else:
                    search = await yt_search.search_query(command)

                if youtube.is_valid(search):  # type: ignore
                    path = await youtube.download_media(search, not video_mode)  # type: ignore
                    if path:
                        await start_stream(msg, path, video_mode, basename(path))
                        return

    await msg.edit(_.translate_chat('streamNoSrc', cid=message.chat.id))
