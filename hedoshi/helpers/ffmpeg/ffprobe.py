# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from subprocess import run, PIPE
from typing import Optional
from pytgcalls.types.raw import VideoParameters


def get_duration(path: str) -> Optional[int]:
    res = run(
        " ".join(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                f'"{path}"',
            ]
        ),
        shell=True,
        stdout=PIPE,
        stderr=PIPE,
    )

    print(res.stderr.decode())
    return int(float(res.stdout.decode()))


def get_resolution(path: str) -> VideoParameters:
    res = run(
        " ".join(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v",
                "-show_entries",
                "stream=width,height,r_frame_rate",
                "-of",
                "csv=p=0:s=x",
                f'"{path}"',
            ]
        ),
        shell=True,
        stdout=PIPE,
        stderr=PIPE,
    )

    print(res.stderr.decode())
    output = res.stdout.decode()
    out_split = output.split("x")
    rate_split = out_split[2].split("/")
    rate_parsed = int(int(rate_split[0]) / int(rate_split[1]))

    return VideoParameters(
        width=int(out_split[0]),
        height=int(out_split[1]),
        frame_rate=rate_parsed,
    )
