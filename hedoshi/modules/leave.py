from pyrogram.types import Message
from ..helpers.telegram.cmd_register import register
from ..helpers.telegram.groups import find_active_userbot
from .. import bot, translator as _


@register(cmd='leave')
async def leave_call(message: Message):
    userbot = await find_active_userbot(message)
    if userbot:
        try:
            await userbot.leave_group_call(message.chat.id)
        except:
            pass

    await bot.send_message(
        message.chat.id,
        text=_.translate_chat('streamEnd', cid=message.chat.id)
    )
