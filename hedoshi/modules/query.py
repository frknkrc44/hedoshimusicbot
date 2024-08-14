# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from pyrogram.types import Message

from .. import translator as _
from ..helpers.format import time_format
from ..helpers.query import get_queries_by_chat
from ..helpers.telegram.cmd_register import register
from ..helpers.telegram.groups import get_current_duration
from ..helpers.telegram.msg_funcs import reply_message


@register(cmd='query|sira')
async def lquery(message: Message):
    out = ''
    query = get_queries_by_chat(message.chat.id)

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
            current = f'{time_format(await get_current_duration(message))}/' if i == 0 else ''
            duration = _.translate_chat(
                'queryDuration',
                args=[f'{current}{time_format(item.duration)}'],
                cid=item.chat_id,
            )
            out = out + f"**{num}**\n{query[i].file_name}\n{duration}\n\n"

    await reply_message(message, out)

'''
@register(cmd='qdel|ssil')
async def dquery(message: Message):
    pass
'''
