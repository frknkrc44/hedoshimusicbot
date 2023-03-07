from pyrogram.types import Message
from pytgcalls.types import AudioPiped, AudioVideoPiped, HighQualityAudio, HighQualityVideo
from ..helpers.cmd_register import register
from ..helpers.groups import join_or_change_stream, find_active_userbot_client, get_client
from .. import bot
from time import time
from logging import info

globals()['last_percent'] = -1
globals()['last_percent_epoch'] = 0


@register(cmd='play|oynat|baslat')
async def play(message: Message):
    msg = await message.reply_text('Processing...')

    if message.reply_to_message:
        reply = message.reply_to_message
        is_audio = reply.audio is not None or reply.voice is not None
        is_video = reply.video is not None or (
            reply.document and reply.document.mime_type.startswith('video'))

        await download_and_start_tg_media(msg, reply, is_video=False)
        if is_audio or is_video:
            return
    else:
        if len(message.command) > 1:
            return

    await msg.edit('No source specified!')


@register(cmd='vplay|voynat|vbaslat')
async def vplay(message: Message):
    msg = await message.reply_text('Processing...')

    if message.reply_to_message:
        reply = message.reply_to_message
        is_audio = reply.audio is not None or reply.voice is not None
        is_video = reply.video is not None or (
            reply.document and reply.document.mime_type.startswith('video'))

        await download_and_start_tg_media(msg, reply, is_video=is_video)
        if is_audio or is_video:
            return
    else:
        if len(message.command) > 1:
            return

    await msg.edit('No source specified!')


async def download_and_start_tg_media(
    reply: Message,
    source: Message,
    use_userbot: bool = False,
    is_video: bool = False,
):
    async def progress_func(current: int, total: int):
        percent = int((current / total) * 100)
        last_percent = globals()['last_percent']
        last_epoch: int = globals()['last_percent_epoch']
        current_epoch = int(time())
        info(f'{last_epoch} - {current_epoch} - {last_epoch - current_epoch}')
        if percent > last_percent and (current_epoch - last_epoch) > 3:
            globals()['last_percent'] = percent
            globals()['last_percent_epoch'] = current_epoch
            try:
                await reply.edit(f'Downloading... {percent}%')
            except:
                pass

    globals()['last_percent'] = -1
    globals()['last_percent_epoch'] = 0

    if use_userbot:
        userbot = await find_active_userbot_client(reply)
        if userbot:
            path = await userbot.download_media(source, progress=progress_func)
        else:
            await reply.edit('No active userbot found, falling back to bot downloader!')
            return await download_and_start_tg_media(
                reply=reply,
                source=source,
                use_userbot=False,
                is_video=is_video,
            )
    else:
        path = await bot.download_media(source, progress=progress_func)

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
        await reply.edit('Stream started!')
        return
    else:
        await reply.edit('Failed to download audio file from Telegram :(')
        return
