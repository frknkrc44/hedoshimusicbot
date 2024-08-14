# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from pyrogram.types import Message

from ..translations import translator as _
from ..helpers.query import get_queries_by_chat, remove_query_by_chat
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
            current = await get_current_duration(message) if i == 0 else None
            details = item.query_details(current_duration=current)
            out = out + f"**{num}**\n{details}\n\n"

    await reply_message(message, out)

@register(
    cmd="qdel|ssil",
    min_args=1,
)
async def dquery(message: Message):
    try:
        idx = int(message.command[1])
    except BaseException:
        pass
    else:
        result = remove_query_by_chat(message.chat.id, idx)

        await reply_message(
            message,
            _.translate_chat(
                "queryDelSuccess" if result else "queryDelFail",
                cid=message.chat.id,
            ),
        )
