from functools import lru_cache
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

    def contains_link_or_requester(self, chat_id: int, link: str, requester_id: int):
        return next(
            (
                item
                for item in self
                if item.chat_id == chat_id
                and (item.link == link or item.requester_id == requester_id)
            ),
            None,
        )

    def remove_pre_query(self, chat_id: int, link: str, requester_id: int):
        found = next(
            (
                item
                for item in self
                if item.chat_id == chat_id
                and (item.link == link or item.requester_id == requester_id)
            ),
            None,
        )

        if found:
            info(f"Removing {found} from the pre query")
            self.remove(found)


__query = PreQueryList()


@lru_cache()
def __is_spam_protection_enabled() -> bool:
    from ..bot_config import values

    return values.get("BOT_USE_SPAM_PROTECTION", "False") == "True"


def __is_requested(chat_id: int, link: str, requester_id: int):
    protection_enabled = __is_spam_protection_enabled()
    if not protection_enabled:
        return False

    return __query.contains_link_or_requester(chat_id, link, requester_id)


def get_pre_queries_by_chat(chat_id: int):
    return [item for item in __query if item.chat_id == chat_id]


def insert_pre_query(chat_id: int, link: str, requester_id: int):
    if __is_requested(chat_id, link, requester_id):
        return True

    __query.append(PreQueryItem(chat_id, link, requester_id))
    return False


def remove_pre_query(chat_id: int, link: str, requester_id: int):
    return __query.remove_pre_query(chat_id, link, requester_id)
