# Copyright (C) 2023 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from pytgcalls.types import AudioPiped, AudioVideoPiped
from json import dumps
from os import sep
from typing import Optional
from .format import time_format

class QueryItem:
    def __init__(
        self,
        stream: AudioPiped | AudioVideoPiped,
        duration: int,
        skip: int,
        chat_id: int,
        loop: bool = False,
    ):
        self.stream = stream
        self.duration = duration
        self.skip = skip
        self.chat_id = chat_id
        self.loop = loop

    def __str__(self) -> str:
        return dumps({
            "stream": self.stream._path,
            "duration": self.duration,
            "skip": self.skip,
            "chat_id": self.chat_id,
            "loop": self.loop,
        })

    def query_details(self, current_duration: Optional[int] = None):
        name = self.stream._path.split(sep)[-1].split('.', 1)[0]
        duration = time_format(self.duration)

        if current_duration:
            duration = f'{time_format(current_duration)}/' + duration

        return f'{name}\n{duration}'
