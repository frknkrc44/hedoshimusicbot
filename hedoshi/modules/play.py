# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from pyrogram.types import Message

from ..helpers.spotify import is_spotify_track
from ..helpers.telegram.cmd_register import register
from ..helpers.telegram.downloader import (download_and_start_tg_media,
                                           parse_telegram_url,
                                           parse_telegram_url_and_stream,
                                           start_stream)
from ..helpers.telegram.groups import add_userbot, find_active_userbot
from ..helpers.telegram.msg_funcs import edit_message, reply_message
from ..helpers.youtube import yt_search
from ..helpers.youtube import ytdl_wrapper as youtube
from ..translations import translator as _


@register(
    cmd="play|oynat|baslat|vplay|voynat|vbaslat",
    bot_admin=True,
)
async def play(message: Message):
    msg = await reply_message(
        message, _.translate_chat("mvProcessing", cid=message.chat.id)
    )
    video_mode = message.command[0].startswith('v')

    calls = await find_active_userbot(message)
    if not calls:
        await edit_message(msg, _.translate_chat("astJoining", cid=message.chat.id))
        try:
            added = await add_userbot(message)
            assert added
        except BaseException:
            await edit_message(
                msg, _.translate_chat("astJoinFail", cid=message.chat.id)
            )
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
                return await parse_telegram_url_and_stream(
                    message, msg, command, video_mode
                )
            elif youtube.is_valid(command) and not is_spotify_track(command):
                path = await youtube.download_media(
                    message, msg, command, not video_mode
                )
                if path:
                    await start_stream(msg, path[0], video_mode, path[1])
                    return
            else:
                if is_spotify_track(command):
                    search = await yt_search.search_from_spotify_link(message, command)
                else:
                    search = await yt_search.search_query(message, command)

                if youtube.is_valid(search):  # type: ignore
                    path = await youtube.download_media(
                        message, msg, search, not video_mode
                    )  # type: ignore
                    if path:
                        await start_stream(msg, path[0], video_mode, path[1])
                        return

    await edit_message(msg, _.translate_chat("streamNoSrc", cid=message.chat.id))
