from logging import info
from typing import Tuple
from pyrogram import Client
from pyrogram.types import Message
from pytgcalls.types import AudioPiped, AudioVideoPiped, HighQualityAudio, HighQualityVideo
from time import time
from re import sub
from .groups import find_active_userbot_client, join_or_change_stream, userbots, get_client
from ... import bot, translator as _


async def _progress_func_wrapper(reply: Message, current: int, total: int):
    percent = int((current / total) * 100)
    last_percent = globals()['last_percent']
    last_epoch: int = globals()['last_percent_epoch']
    current_epoch = int(time())
    info(f'{last_epoch} - {current_epoch} - {last_epoch - current_epoch}')
    if percent > last_percent and (current_epoch - last_epoch) > 3:
        globals()['last_percent'] = percent
        globals()['last_percent_epoch'] = current_epoch
        try:
            await reply.edit(_.translate_chat('mvDownloading', args=[percent], cid=reply.chat.id))
        except:
            pass


def parse_telegram_url(url: str) -> Tuple[str | int | None] | None:
    valid_telegram_domains = [
        't.me', 'telegram.org', 'telegram.dog'
    ]

    new_url = sub('https?://', '', url)
    splitter = new_url.split('/')

    if not splitter[0] in valid_telegram_domains:
        return (None, None)  # type: ignore

    increaser = 1 if 's' in splitter or 'c' in splitter else 0
    try:
        chat_id = int('-100' + splitter[1 + increaser])
    except:
        chat_id = splitter[1 + increaser]  # type: ignore

    msg_id = int(splitter[2 + increaser])
    return (chat_id, msg_id)  # type: ignore


async def parse_telegram_url_and_stream(reply: Message, url: str, is_video: bool):
    cid, mid = parse_telegram_url(url)  # type: ignore
    print(cid, mid)

    if not cid or not mid:
        return

    for item in userbots:
        client: Client = get_client(item)
        try:
            msg = await client.get_messages(
                chat_id=cid,
                message_ids=mid,
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


async def download_and_start_tg_media(
    reply: Message,
    source: Message,
    use_userbot: bool = False,
    userbot: Client | None = None,
    is_video: bool = False,
):
    globals()['last_percent'] = -1
    globals()['last_percent_epoch'] = 0

    async def progress_func(current: int, total: int):
        return await _progress_func_wrapper(reply, current, total)

    if use_userbot:
        if not userbot:
            userbot = await find_active_userbot_client(reply)

        if userbot:
            path = await userbot.download_media(source, progress=progress_func)
        else:
            await reply.edit(_.translate_chat('streamDLNoUserbot', cid=reply.chat.id))
            return await download_and_start_tg_media(
                reply=reply,
                source=source,
                use_userbot=False,
                is_video=is_video,
            )
    else:
        path = await bot.download_media(source, progress=progress_func)

    await start_stream(reply, path, is_video)  # type: ignore


async def start_stream(reply: Message, path: str, is_video: bool):
    if path:
        item = await join_or_change_stream(
            reply,
            AudioVideoPiped(
                path,
                audio_parameters=HighQualityAudio(),
                video_parameters=HighQualityVideo(),
            ) if is_video else AudioPiped(
                path,
                audio_parameters=HighQualityAudio(),
            ),
        )
        if item:
            await reply.edit(_.translate_chat('streamQueryAdded', cid=reply.chat.id))
        else:
            await reply.edit(_.translate_chat('streamStarted', cid=reply.chat.id))
        return
    else:
        await reply.edit(_.translate_chat('streamTGError', cid=reply.chat.id))
        return