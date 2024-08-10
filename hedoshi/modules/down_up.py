# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from pyrogram.types import Message
from ..helpers.telegram.cmd_register import register
from ..helpers.telegram.downloader import (
    download_tg_media,
    parse_telegram_url_and_download,
    parse_telegram_url,
    _progress_func_wrapper,
)
from ..helpers.youtube import ytdl_wrapper as youtube, yt_search
from .. import translator as _
from os.path import basename


@register(cmd='down|udown|indir|uindir')
async def download(message: Message):
    msg = await message.reply_text(_.translate_chat('mvProcessing', cid=message.chat.id))
    upload_mode = message.command[0].startswith('u')

    async def progress_func(current: int, total: int):
        return await _progress_func_wrapper(msg, current, total, upload=True)

    async def upload_file_or_send_message(path: str) -> None:
        upload_path = f'downloads/{basename(path)}'
        if upload_mode:
            await message.reply_document(
                path,
                caption=basename(path),
                progress=progress_func,
            )
            await msg.edit(_.translate_chat('mvUploaded', cid=message.chat.id, args=[upload_path]))
        else:
            await msg.edit(_.translate_chat('mvDownloaded', cid=message.chat.id, args=[upload_path]))

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
                path = await youtube.download_media(command)
                if path:
                    return await upload_file_or_send_message(path)
            else:
                if search := await yt_search.search_query(command):
                    if youtube.is_valid(search):
                        path = await youtube.download_media(search)
                        if path:
                            return await upload_file_or_send_message(path)

    await msg.edit(_.translate_chat('streamNoSrc', cid=message.chat.id))
