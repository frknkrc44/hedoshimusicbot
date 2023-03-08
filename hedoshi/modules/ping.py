from pyrogram.types import Message
from ..helpers.telegram.cmd_register import register
from time import time


@register('ping|check', private=True)
async def ping(message: Message) -> None:
    start = time()
    msg = await message.reply_text('Pong!')
    delta = time() - start
    await msg.edit(f'Pong! - {delta*1000:.0f}ms')
