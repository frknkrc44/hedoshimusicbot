from json import dumps
from logging import info
from typing import List


class PreQueryItem:
    def __init__(self, chat_id: int, link: str, requester_id: int) -> None:
        self.chat_id = chat_id
        self.link = link
        self.requester_id = requester_id

    def __str__(self) -> str:
        return dumps(
            {
                "chat_id": self.chat_id,
                "link": self.link,
                "requester_id": self.requester_id,
            }
        )


class PreQueryList(List[PreQueryItem]):
    def append(self, object: PreQueryItem) -> None:
        info(f"Adding {object} to the pre query")
        return super().append(object)

    def pre_queries_by_chat(self, chat_id: int) -> List[PreQueryItem]:
        return [item for item in self if item.chat_id == chat_id]

    def contains_chat_link(self, chat_id: int, link: str):
        return next(
            (item for item in self if item.chat_id == chat_id and item.link == link),
            None,
        )

    def remove_pre_query(self, chat_id: int, link: str):
        found = next(
            (item for item in self if item.chat_id == chat_id and item.link == link),
            None,
        )

        if found:
            info(f"Removing {found} from the pre query")
            self.remove(found)


__query = PreQueryList()


def __is_requested(chat_id: int, link: str):
    return __query.contains_chat_link(chat_id, link)


def get_pre_queries_by_chat(chat_id: int):
    return [item for item in __query if item.chat_id == chat_id]


def insert_pre_query(chat_id: int, link: str, requester_id: int):
    if __is_requested(chat_id, link):
        return True

    __query.append(PreQueryItem(chat_id, link, requester_id))
    return False


def remove_pre_query(chat_id: int, link: str):
    return __query.remove_pre_query(chat_id, link)
