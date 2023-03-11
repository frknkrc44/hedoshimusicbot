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


def replace_query(old_item: QueryItem, new_item: QueryItem):
    idx = query.index(old_item)
    query.pop(idx)
    query.insert(idx, new_item)
