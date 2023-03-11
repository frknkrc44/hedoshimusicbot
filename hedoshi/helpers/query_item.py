from pytgcalls.types import AudioPiped, AudioVideoPiped
from json import dumps


class QueryItem:
    def __init__(
        self,
        stream: AudioPiped | AudioVideoPiped,
        duration: int,
        skip: int,
        chat_id: int,
    ):
        self.stream = stream
        self.duration = duration
        self.skip = skip
        self.chat_id = chat_id

    def __str__(self) -> str:
        return dumps({
            "stream": self.stream._path,
            "duration": self.duration,
            "skip": self.skip,
            "chat_id": self.chat_id,
        })
