from pyrogram.types import Message
from ..helpers.telegram.cmd_register import register
from ..helpers.telegram.groups import find_active_userbot
from ..helpers.query import clear_query
from .. import translator as _


@register(cmd='leave|ayril|end|son')
async def leave_call(message: Message):
    userbot = await find_active_userbot(message)
    if userbot:
        try:
            clear_query(message.chat.id)
            await userbot.leave_group_call(message.chat.id)
        except:
            pass

    await message.reply(
        text=_.translate_chat('streamEnd', cid=message.chat.id)
    )
