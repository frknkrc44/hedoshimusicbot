from logging import info
from pyrogram.types import Message
from pytgcalls.types import AudioPiped, AudioVideoPiped, HighQualityAudio, HighQualityVideo
from time import time
from .groups import find_active_userbot_client, join_or_change_stream
from ... import bot, translator as _


async def progress_func(reply: Message, current: int, total: int):
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


async def download_and_start_tg_media(
    reply: Message,
    source: Message,
    use_userbot: bool = False,
    is_video: bool = False,
):
    globals()['last_percent'] = -1
    globals()['last_percent_epoch'] = 0

    if use_userbot:
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
        await join_or_change_stream(
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
        await reply.edit(_.translate_chat('streamStarted', cid=reply.chat.id))
        return
    else:
        await reply.edit(_.translate_chat('streamTGError', cid=reply.chat.id))
        return
