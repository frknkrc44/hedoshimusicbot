from pyrogram.types import Message
from ..helpers.telegram.cmd_register import register
from ..helpers.telegram.groups import find_active_userbot
from .. import translator as _


@register(cmd='resume|devam')
async def play(message: Message):
    userbot = await find_active_userbot(message)
    if userbot:
        try:
            await userbot.resume_stream(message.chat.id)
            await message.reply(_.translate_chat('streamResumed', cid=message.chat.id))
        except:
            pass


@register(cmd='pause|duraklat')
async def pause(message: Message):
    userbot = await find_active_userbot(message)
    if userbot:
        try:
            await userbot.pause_stream(message.chat.id)
            await message.reply(_.translate_chat('streamPaused', cid=message.chat.id))
        except:
            pass
