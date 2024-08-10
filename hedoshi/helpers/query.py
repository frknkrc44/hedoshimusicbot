# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from logging import info
from os import remove as remove_file
from typing import List, Optional
from .query_item import QueryItem

class QueryList(List[QueryItem]):
    def media_in_use(self, value: QueryItem) -> bool:
        for i in self:
            if value != i and i.stream._media_path == value.stream._media_path:
                return True

        return False

    def pop_item(self, index: int) -> QueryItem:
        item = self[index]
        self.remove_item(item)
        return item

    def remove_item(self, value: QueryItem) -> None:
        from .. import bot_config

        remove_file_enabled = (
            bot_config.BOT_REMOVE_FILE_AUTO
            if hasattr(bot_config, "BOT_REMOVE_FILE_AUTO")
            else False
        )

        if remove_file_enabled and not self.media_in_use(value):
            info(
                f"Auto-remove enabled and the media not in use, removing {value.stream._media_path}"
            )
            remove_file(value.stream._media_path)

        self.remove(value)


query = QueryList()


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
        return query.pop_item(first_index)

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
        query.remove_item(item)


def replace_query(old_item: QueryItem, new_item: QueryItem) -> None:
    idx = query.index(old_item)
    query.pop(idx)
    query.insert(idx, new_item)
