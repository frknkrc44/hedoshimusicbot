# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE


async def merge_files(audio_file: str, video_file: str, target_file: str) -> bool:
    process = await create_subprocess_exec(
        "ffmpeg",
        "-i",
        audio_file,
        "-i",
        video_file,
        "-c",
        "copy",
        target_file,
        stdout=PIPE,
        stderr=PIPE,
    )

    _ = await process.communicate()

    return process.returncode == 0
