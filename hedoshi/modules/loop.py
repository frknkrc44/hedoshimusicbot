from ..helpers import get_next_query
from ..helpers.telegram.cmd_register import register
from pyrogram.types import Message


@register(cmd='loop')
async def set_loop(message: Message):
    item = get_next_query(message.chat.id)
    if not item:
        await message.reply('No playing song!')
        return

    if not item.loop:
        item.loop = True
        await message.reply('Loop ON')
    else:
        item.loop = False
        await message.reply('Loop OFF')
