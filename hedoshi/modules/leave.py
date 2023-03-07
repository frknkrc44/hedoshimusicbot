from pyrogram.types import Message
from ..helpers.cmd_register import register
from ..helpers.groups import find_active_userbot

@register(cmd='leave')
async def leave_call(message: Message):
    userbot = await find_active_userbot(message)
    if userbot:
        try:
            await userbot.leave_group_call(message.chat.id)
        except:
            pass