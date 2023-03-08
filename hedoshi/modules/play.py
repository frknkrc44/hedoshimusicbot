from pyrogram.types import Message
from ..helpers.telegram.cmd_register import register
from ..helpers.telegram.downloader import (download_and_start_tg_media, start_stream,
                                           parse_telegram_url, parse_telegram_url_and_stream)
from ..helpers.youtube import ytdl_wrapper as youtube
from .. import translator as _


@register(cmd='play|oynat|baslat')
async def play(message: Message):
    msg = await message.reply_text(_.translate_chat('mvProcessing', cid=message.chat.id))

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
            if parse_telegram_url(message.command[1])[0]:  # type: ignore
                await parse_telegram_url_and_stream(msg, message.command[1], False)
            elif youtube.is_valid(message.command[1]):
                path = youtube.download_media(message.command[1], msg, True)
                await start_stream(msg, path, False)
            else:
                await msg.edit(_.translate_chat('streamNoSrc', cid=message.chat.id))
            return

    await msg.edit(_.translate_chat('streamNoSrc', cid=message.chat.id))
