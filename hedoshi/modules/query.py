# Copyright (C) 2023 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from os import sep
from pyrogram.types import Message
from ..helpers.telegram.cmd_register import register
from ..helpers.telegram.groups import query, get_current_duration
from .. import translator as _
from ..helpers.format import time_format


@register(cmd='query|sira')
async def lquery(message: Message):
    out = ''
    if not len(query):
        out = _.translate_chat('queryEmpty', cid=message.chat.id)
    else:
        def show_current_or_number(num: int) -> str:
            return _.translate_chat('queryCurrent', cid=item.chat_id) \
                if num == 0 \
                else _.translate_chat('queryNum', cid=item.chat_id, args=[num])

        for i in range(len(query)):
            item = query[i]
            num = show_current_or_number(i)
            name = item.stream._path.split(sep)[-1]
            name = name[:name.find('.')]
            current = f'{time_format(await get_current_duration(message))}/' if i == 0 else ''
            duration = _.translate_chat(
                'queryDuration',
                args=[f'{current}{time_format(item.duration)}'],
                cid=item.chat_id,
            )
            out = out + f'**{num}**\n{name}\n{duration}\n\n'

    await message.reply(out)

'''
@register(cmd='qdel|ssil')
async def dquery(message: Message):
    pass
'''
