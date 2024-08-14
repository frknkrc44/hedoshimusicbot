# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from json import dumps
from typing import Optional

from pytgcalls.types import MediaStream

from .format import time_format
from ..translations import translator as _


class QueryItem:
    def __init__(
        self,
        stream: MediaStream,
        duration: int,
        skip: int,
        chat_id: int,
        file_name: str,
        loop: bool = False,
        video: bool = False,
    ):
        self.stream = stream
        self.duration = duration
        self.skip = skip
        self.chat_id = chat_id
        self.file_name = file_name
        self.loop = loop
        self.video = video

    def __str__(self) -> str:
        return dumps(
            {
                "stream": self.stream._media_path,
                "duration": self.duration,
                "skip": self.skip,
                "chat_id": self.chat_id,
                "file_name": self.file_name,
                "loop": self.loop,
                "video": self.video,
            }
        )

    def query_details(self, current_duration: Optional[int] = None):
        duration = time_format(self.duration)

        if current_duration:
            duration = f"{time_format(current_duration)}/{duration}"

        return QueryItem.query_details_static(
            self.chat_id,
            self.file_name,
            duration,
        )

    @staticmethod
    def query_details_static(chat_id: int, file_name: str, duration: str):
        duration_text = _.translate_chat(
            "queryDuration",
            cid=chat_id,
            args=[duration],
        )
        return f"{file_name}\n{duration_text}"
