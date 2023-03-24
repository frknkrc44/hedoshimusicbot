# Copyright (C) 2020-2023 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from subprocess import run, PIPE
from typing import Optional


async def get_duration(path: str) -> Optional[int]:
    res = run(' '.join(["ffprobe",
                        "-v",
                        "error",
                        "-show_entries",
                        "format=duration",
                        "-of",
                        "default=noprint_wrappers=1:nokey=1",
                        f'"{path}"',
                        ]), shell=True, stdout=PIPE,)
    return int(float(res.stdout.decode()))
