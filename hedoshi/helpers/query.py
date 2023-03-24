# Copyright (C) 2020-2023 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from typing import List, Optional
from .query_item import QueryItem

query: List[QueryItem] = []


def get_next_query(chat_id: int, delete: bool = False) -> Optional[QueryItem]:
    if not len(query):
        return None

    first_index = -1
    for item in query:
        if item.chat_id == chat_id:
            first_index = query.index(item)
            break

    if first_index < 0:
        return None

    if delete:
        return query.pop(first_index)

    return query[first_index]


def clear_query(chat_id: int) -> None:
    if not len(query):
        return

    remove = []
    for item in query:
        if item.chat_id == chat_id:
            remove.append(item)

    if not len(remove):
        return

    for item in remove:
        query.remove(item)


def replace_query(old_item: QueryItem, new_item: QueryItem) -> None:
    idx = query.index(old_item)
    query.pop(idx)
    query.insert(idx, new_item)
