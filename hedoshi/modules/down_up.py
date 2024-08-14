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

from .. import translator as _
from ..helpers.spotify import is_spotify_track
from ..helpers.telegram.cmd_register import register
from ..helpers.telegram.downloader import (download_tg_media,
                                           parse_telegram_url,
                                           parse_telegram_url_and_download,
                                           upload_tg_media)
from ..helpers.telegram.msg_funcs import edit_message, reply_message
from ..helpers.youtube import yt_search
from ..helpers.youtube import ytdl_wrapper as youtube


@register(cmd='down|udown|indir|uindir')
async def download(message: Message):
    msg = await reply_message(_.translate_chat("mvProcessing", cid=message.chat.id))
    upload_mode = message.command[0].startswith('u')

    async def upload_file_or_send_message(path: str) -> None:
        upload_path = f'downloads/{basename(path)}'
        if upload_mode:
            await upload_tg_media(msg, path)
            await edit_message(
                msg,
                _.translate_chat("mvUploaded", cid=message.chat.id, args=[upload_path]),
            )
        else:
            await edit_message(
                msg,
                _.translate_chat(
                    "mvDownloaded", cid=message.chat.id, args=[upload_path]
                ),
            )

    if message.reply_to_message:
        reply = message.reply_to_message
        is_audio = reply.audio is not None or reply.voice is not None or (
            reply.document and 'audio' in reply.document.mime_type)
        is_video = reply.video is not None or (
            reply.document and 'video' in reply.document.mime_type)

        if is_audio or is_video:
            path = await download_tg_media(msg, reply)
            if path:
                return await upload_file_or_send_message(path)
    else:
        if len(message.command) > 1:
            command = ' '.join(message.command[1:])
            if parse_telegram_url(command)[0]:
                path = await parse_telegram_url_and_download(msg, command)
                if path:
                    return await upload_file_or_send_message(path)
            elif youtube.is_valid(command):
                path = await youtube.download_media(msg, command)
                if path:
                    return await upload_file_or_send_message(path[0])
            else:
                if is_spotify_track(command):
                    search = await yt_search.search_from_spotify_link(command)
                else:
                    search = await yt_search.search_query(command)

                if youtube.is_valid(search):
                    path = await youtube.download_media(msg, search)
                    if path:
                        return await upload_file_or_send_message(path[0])

    await edit_message(msg, _.translate_chat("streamNoSrc", cid=message.chat.id))
