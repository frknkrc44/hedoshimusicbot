# Copyright (C) 2023 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from os import sep, getcwd, listdir
from typing import Optional, Tuple
from pyrogram import Client
from pyrogram.enums import MessageMediaType
from pyrogram.types import Message
from pytgcalls.types import MediaStream, VideoQuality
from pytgcalls.types.raw import VideoParameters
from time import time
from re import sub
from .groups import find_active_userbot_client, join_or_change_stream, userbots, get_client
from ... import translator as _
from ..ffmpeg.ffprobe import get_resolution

async def _progress_func_wrapper(reply: Message, current: int, total: int, upload: bool = False) -> None:
    percent = int((current / total) * 100)
    last_percent = globals()['last_percent']
    last_epoch: int = globals()['last_percent_epoch']
    current_epoch = int(time())
    if percent > last_percent and (current_epoch - last_epoch) > 3:
        globals()['last_percent'] = percent
        globals()['last_percent_epoch'] = current_epoch
        try:
            await reply.edit(_.translate_chat('mvUploading' if upload else 'mvDownloading', args=[percent], cid=reply.chat.id))
        except BaseException:
            pass


def parse_telegram_url(url: str) -> Optional[Tuple[str | int | None]]:
    valid_telegram_domains = [
        't.me', 'telegram.org', 'telegram.dog'
    ]

    new_url = sub('https?://', '', url)
    splitter = new_url.split('/')

    if splitter[0] not in valid_telegram_domains:
        return (None, None, None)  # type: ignore

    increaser = 1 if 's' in splitter or 'c' in splitter else 0
    try:
        chat_id = int('-100' + splitter[1 + increaser])
    except BaseException:
        chat_id = splitter[1 + increaser]  # type: ignore

    msg_id = int(splitter[-1])
    topic_id = int(splitter[-2]) if len(splitter) > (increaser + 3) else None

    return (chat_id, msg_id, topic_id)  # type: ignore


async def parse_telegram_url_and_stream(reply: Message, url: str, is_video: bool) -> None:
    chat_id, message_id, _ = parse_telegram_url(url)  # type: ignore

    if not chat_id or not message_id:
        return

    for item in userbots:
        client: Client = get_client(item)

        try:
            msg = await client.get_messages(
                chat_id=chat_id,
                message_ids=message_id,
            )
            await download_and_start_tg_media(
                reply=reply,
                source=msg,  # type: ignore
                use_userbot=True,
                userbot=client,
                is_video=is_video,
            )
            return
        except BaseException as e:
            raise e

    await reply.edit(
        _.translate_chat('streamTGError', cid=reply.chat.id))  # type: ignore


async def parse_telegram_url_and_download(reply: Message, url: str) -> Optional[str]:
    chat_id, message_id, _ = parse_telegram_url(url)  # type: ignore

    if not chat_id or not message_id:
        return None

    for item in userbots:
        client: Client = get_client(item)

        try:
            msg = await client.get_messages(
                chat_id=chat_id,
                message_ids=message_id,
            )
            return await download_tg_media(
                reply=reply,
                source=msg,  # type: ignore
                use_userbot=True,
                userbot=client,
            )
        except BaseException as e:
            raise e

    await reply.edit(
        _.translate_chat('streamTGError', cid=reply.chat.id))  # type: ignore
    return None


def get_downloaded_file_name(source: Message) -> Optional[str]:
    download_dir = f'{getcwd()}{sep}downloads'

    match source.media:
        case MessageMediaType.AUDIO:
            if source.audio.file_name in listdir(download_dir):
                return f'{download_dir}{sep}{source.audio.file_name}'
        case MessageMediaType.DOCUMENT:
            if source.document.file_name in listdir(download_dir):
                return f'{download_dir}{sep}{source.document.file_name}'
        case MessageMediaType.VIDEO:
            if source.video.file_name in listdir(download_dir):
                return f'{download_dir}{sep}{source.video.file_name}'

    return None


async def download_tg_media(
    reply: Message,
    source: Message,
    use_userbot: bool = False,
    userbot: Optional[Client] = None,
) -> Optional[str]:
    globals()['last_percent'] = -1
    globals()['last_percent_epoch'] = 0

    async def progress_func(current: int, total: int):
        return await _progress_func_wrapper(reply, current, total)

    if use_userbot:
        if not userbot:
            userbot = await find_active_userbot_client(reply)

        if userbot:
            path = get_downloaded_file_name(source) or (
                await userbot.download_media(source, progress=progress_func))
        else:
            await reply.edit(_.translate_chat('streamDLNoUserbot', cid=reply.chat.id))
            return await download_tg_media(
                reply=reply,
                source=source,
                use_userbot=False,
                userbot=userbot,
            )
    else:
        path = get_downloaded_file_name(source) or (
            await reply._client.download_media(source, progress=progress_func))

    return path  # type: ignore


async def upload_tg_media(
    reply: Message,
    path: str,
    use_userbot: bool = False,
    userbot: Optional[Client] = None,
):
    async def progress_func(current: int, total: int):
        return await _progress_func_wrapper(reply, current, total, True)

    if use_userbot:
        if not userbot:
            userbot = await find_active_userbot_client(reply)

        if userbot:
            return await userbot.send_document(
                chat_id=reply.chat.id, 
                document=path, 
                progress=progress_func, 
                reply_to_message_id=reply.id,
            )
        else:
            await reply.edit(_.translate_chat('streamDLNoUserbot', cid=reply.chat.id))
            return await upload_tg_media(
                reply=reply,
                path=path,
                use_userbot=False,
                userbot=userbot,
            )
    else:
        return await reply.reply_document(path, progress=progress_func)


async def download_and_start_tg_media(
    reply: Message,
    source: Message,
    use_userbot: bool = False,
    userbot: Client | None = None,
    is_video: bool = False,
) -> None:
    path = await download_tg_media(reply, source, use_userbot, userbot)

    params: Optional[VideoParameters] = None
    if is_video:
        raw_res = get_resolution(path)
        params = VideoParameters(
            width=raw_res[0],
            height=raw_res[1],
            frame_rate=raw_res[2],
        )

    await start_stream(reply, path, is_video, params)  # type: ignore


async def start_stream(
    reply: Message,
    path: str,
    is_video: bool,
    video_params: VideoParameters = None,
) -> None:
    if path:
        item = await join_or_change_stream(
            reply,
            MediaStream(
                path,
                video_flags=MediaStream.Flags.IGNORE
                if not is_video
                else MediaStream.Flags.AUTO_DETECT,
                video_parameters=video_params or VideoQuality.SD_480p,
            ),
            video=is_video,
        )
        if item:
            await reply.edit(_.translate_chat('streamQueryAdded', cid=reply.chat.id))
        else:
            await reply.edit(_.translate_chat('streamStarted', cid=reply.chat.id))
        return
    else:
        await reply.edit(_.translate_chat('streamTGError', cid=reply.chat.id))
        return
