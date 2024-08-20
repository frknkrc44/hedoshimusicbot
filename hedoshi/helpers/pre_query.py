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
    def pre_queries_by_chat(self, chat_id: int) -> List[PreQueryItem]:
        return [item for item in self if item.chat_id == chat_id]

    def contains_link_or_requester(self, chat_id: int, link: str, requester_id: int):
        pre_query = self.pre_queries_by_chat(chat_id)

        link_found = any(item.link == link for item in pre_query)
        requester_found = any(item.requester_id == requester_id for item in pre_query)

        return link_found or requester_found

    def remove_pre_query(self, chat_id: int, link: str, requester_id: int):
        items_removing = []

        for item in self:
            if (
                item.chat_id == chat_id
                and item.link == link
                and item.requester_id == requester_id
            ):
                items_removing.append(item)

        for item in items_removing:
            info(f"Removing {item} from pre query")
            self.remove(item)


__query = PreQueryList()


def is_requested(chat_id: int, link: str, requester_id: int):
    return __query.contains_link_or_requester(chat_id, link, requester_id)


def insert_pre_query(chat_id: int, link: str, requester_id: int):
    if is_requested(chat_id, link, requester_id):
        return True

    __query.append(PreQueryItem(chat_id, link, requester_id))
    return False


def remove_pre_query(chat_id: int, link: str, requester_id: int):
    return __query.remove_pre_query(chat_id, link, requester_id)
