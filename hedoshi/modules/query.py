from pyrogram.types import Message
from ..helpers.telegram.cmd_register import register
from ..helpers.telegram.groups import query
from .. import translator as _


@register(cmd='query|sira')
async def lquery(message: Message):
    out = ''
    if not len(query):
        out = _.translate_chat('queryEmpty', cid=message.chat.id)
    else:
        for i in range(len(query)):
            item = query[i]
            out = out + f'{i} - ' + item.stream._path.split('/')[-1] + '\n'

    await message.reply(out)

'''
@register(cmd='qdel|ssil')
async def dquery(message: Message):
    pass
'''
