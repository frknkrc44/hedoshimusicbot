# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from mimetypes import guess_extension
from os import sep
from os.path import exists
from re import sub
from time import time
from typing import Optional, Tuple

from pyrogram import Client
from pyrogram.enums import MessageMediaType
from pyrogram.types import Message
from pytgcalls.types import MediaStream, VideoQuality

from ...translations import translator as _
from ..ffmpeg.ffprobe import get_audio_params, get_duration, get_resolution
from ..format import time_format
from ..pre_query import insert_pre_query, remove_pre_query
from ..query_item import QueryItem
from .groups import find_active_userbot_client, join_or_change_stream


async def _progress_func_wrapper(reply: Message, current: int, total: int, upload: bool = False) -> None:
    from ... import bot_config

    ignore_progress = (
        bot_config.BOT_IGNORE_PROGRESS
        if hasattr(bot_config, "BOT_IGNORE_PROGRESS")
        else False
    )

    if ignore_progress:
        return

    percent = int((current / total) * 100)
    last_percent = globals().get(f"last_percent_{reply.chat.id}_{reply.id}", -1)
    last_epoch: int = globals().get(f"last_percent_epoch_{reply.chat.id}_{reply.id}", 0)
    current_epoch = int(time())
    if percent > last_percent and (current_epoch - last_epoch) > 3:
        globals()[f"last_percent_{reply.chat.id}_{reply.id}"] = percent
        globals()[f"last_percent_epoch_{reply.chat.id}_{reply.id}"] = current_epoch

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


async def parse_telegram_url_and_stream(
    source: Message,
    reply: Message,
    url: str,
    is_video: bool,
    use_userbot=True,
) -> None:
    if insert_pre_query(
        source.chat.id,
        url,
        source.from_user.id if source.from_user else source.chat.id,
    ):
        return  # type: ignore

    chat_id, message_id, __ = parse_telegram_url(url)  # type: ignore

    if not chat_id or not message_id:
        return

    client: Client = reply._client
    if use_userbot:
        userbot = await find_active_userbot_client(source)
        if userbot:
            client = userbot

    try:
        msg = await client.get_messages(
            chat_id=chat_id,
            message_ids=message_id,
        )

        await download_and_start_tg_media(
            reply=reply,
            source=msg,  # type: ignore
            use_userbot=use_userbot,
            userbot=client,
            is_video=is_video,
        )

        remove_pre_query(
            source.chat.id,
            url,
        )
        return
    except BaseException:
        remove_pre_query(
            source.chat.id,
            url,
        )

        if use_userbot:
            return await parse_telegram_url_and_stream(
                source,
                reply,
                url,
                is_video,
                use_userbot=False,
            )

        await reply.edit(_.translate_chat("streamTGError", cid=reply.chat.id))  # type: ignore


async def parse_telegram_url_and_download(
    source: Message,
    reply: Message,
    url: str,
    use_userbot: bool = True,
) -> Optional[str]:
    if insert_pre_query(
        source.chat.id,
        url,
        source.from_user.id if source.from_user else source.chat.id,
    ):
        return None

    chat_id, message_id, __ = parse_telegram_url(url)  # type: ignore

    if not chat_id or not message_id:
        return None

    client: Client = reply._client
    if use_userbot:
        userbot = await find_active_userbot_client(source)
        if userbot:
            client = userbot

    try:
        msg = await client.get_messages(
            chat_id=chat_id,
            message_ids=message_id,
        )

        ret = await download_tg_media(
            reply=reply,
            source=msg,  # type: ignore
            use_userbot=True,
            userbot=client,
        )

        remove_pre_query(
            source.chat.id,
            url,
        )

        return ret
    except BaseException:
        remove_pre_query(
            source.chat.id,
            url,
        )

        if use_userbot:
            return await parse_telegram_url_and_download(
                source,
                reply,
                url,
                use_userbot=False,
            )

        await reply.edit(_.translate_chat("streamTGError", cid=reply.chat.id))  # type: ignore


def escape_file_name(name: str, id: str):
    return f"downloads{sep}{id}{name[name.rfind('.'):]}"


def __get_raw_file_name(source: Message):
    match source.media:
        case MessageMediaType.AUDIO:
            return source.audio.file_name or __get_file_from_id_mimetype(
                source.audio.file_unique_id,
                source.audio.mime_type,
            )
        case MessageMediaType.DOCUMENT:
            return source.document.file_name or __get_file_from_id_mimetype(
                source.document.file_unique_id,
                source.document.mime_type,
            )
        case MessageMediaType.VIDEO:
            return source.video.file_name or __get_file_from_id_mimetype(
                source.video.file_unique_id,
                source.video.mime_type,
            )

    return None


def __get_file_from_id_mimetype(file_id: str, mime_type: str):
    return f"{file_id}.{guess_extension(mime_type)}"


def get_downloaded_file_name(
    source: Message,
    force_return: bool = False,
) -> Optional[str]:
    match source.media:
        case MessageMediaType.AUDIO:
            escaped_name = escape_file_name(
                source.audio.file_name
                or __get_file_from_id_mimetype(
                    source.audio.file_unique_id,
                    source.audio.mime_type,
                ),
                source.audio.file_unique_id,
            )
            if exists(escaped_name) or force_return:
                return escaped_name
        case MessageMediaType.DOCUMENT:
            escaped_name = escape_file_name(
                source.document.file_name
                or __get_file_from_id_mimetype(
                    source.document.file_unique_id,
                    source.document.mime_type,
                ),
                source.document.file_unique_id,
            )
            if exists(escaped_name) or force_return:
                return escaped_name
        case MessageMediaType.VIDEO:
            escaped_name = escape_file_name(
                source.video.file_name
                or __get_file_from_id_mimetype(
                    source.video.file_unique_id,
                    source.video.mime_type,
                ),
                source.video.file_unique_id,
            )
            if exists(escaped_name) or force_return:
                return escaped_name

    return None


async def download_tg_media(
    reply: Message,
    source: Message,
    use_userbot: bool = False,
    userbot: Optional[Client] = None,
) -> Optional[str]:
    async def progress_func(current: int, total: int):
        return await _progress_func_wrapper(reply, current, total)

    if use_userbot:
        if not userbot:
            userbot = await find_active_userbot_client(reply)

        if userbot:
            path = get_downloaded_file_name(source) or (
                await userbot.download_media(
                    source,
                    progress=progress_func,
                    file_name=get_downloaded_file_name(source, True),
                )
            )

            del globals()[f"last_percent_{reply.chat.id}_{reply.id}"]
            del globals()[f"last_percent_epoch_{reply.chat.id}_{reply.id}"]
        else:
            await reply.edit(_.translate_chat('streamDLNoUserbot', cid=reply.chat.id))
            return await download_tg_media(
                reply=reply,
                source=source,
                use_userbot=False,
            )
    else:
        path = get_downloaded_file_name(source) or (
            await reply._client.download_media(
                source,
                progress=progress_func,
                file_name=get_downloaded_file_name(source, True),
            )
        )

        del globals()[f"last_percent_{reply.chat.id}_{reply.id}"]
        del globals()[f"last_percent_epoch_{reply.chat.id}_{reply.id}"]

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
            ret = await userbot.send_document(
                chat_id=reply.chat.id,
                document=path,
                progress=progress_func,
                reply_to_message_id=reply.id,
            )

            del globals()[f"last_percent_{reply.chat.id}_{reply.id}"]
            del globals()[f"last_percent_epoch_{reply.chat.id}_{reply.id}"]

            return ret
        else:
            await reply.edit(_.translate_chat('streamDLNoUserbot', cid=reply.chat.id))
            ret = await upload_tg_media(
                reply=reply,
                path=path,
                use_userbot=False,
                userbot=userbot,
            )

            del globals()[f"last_percent_{reply.chat.id}_{reply.id}"]
            del globals()[f"last_percent_epoch_{reply.chat.id}_{reply.id}"]

            return ret
    else:
        ret = await reply.reply_document(path, progress=progress_func)

        del globals()[f"last_percent_{reply.chat.id}_{reply.id}"]
        del globals()[f"last_percent_epoch_{reply.chat.id}_{reply.id}"]

        return ret


async def download_and_start_tg_media(
    reply: Message,
    source: Message,
    use_userbot: bool = False,
    userbot: Client | None = None,
    is_video: bool = False,
) -> None:
    path = await download_tg_media(reply, source, use_userbot, userbot)

    await start_stream(
        reply,
        path,
        is_video,
        __get_raw_file_name(source),
    )  # type: ignore


async def start_stream(
    reply: Message,
    path: str,
    is_video: bool,
    file_name: str,
) -> None:
    if path:
        video_params = get_resolution(path) if is_video else None
        audio_params = get_audio_params(path)

        item = await join_or_change_stream(
            reply,
            MediaStream(
                path,
                video_flags=MediaStream.Flags.IGNORE
                if not is_video
                else MediaStream.Flags.AUTO_DETECT,
                audio_parameters=audio_params,
                video_parameters=video_params or VideoQuality.SD_480p,
            ),
            file_name,
            video=is_video,
        )

        arg: Optional[str] = None
        try:
            arg = QueryItem.query_details_static(
                reply.chat.id,
                file_name,
                time_format(get_duration(path)),
            )
        except BaseException:
            pass

        await reply.edit(
            _.translate_chat(
                "streamQueryAdded" if item else "streamStarted",
                cid=reply.chat.id,
                args=[arg],
            ),
        )
    else:
        await reply.edit(_.translate_chat('streamTGError', cid=reply.chat.id))
        return
