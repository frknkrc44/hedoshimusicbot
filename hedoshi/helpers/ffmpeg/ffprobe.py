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
from pytgcalls.types.raw import AudioParameters, VideoParameters


def get_duration(path: str) -> Optional[int]:
    res = run(
        " ".join(
            [
                "ffprobe",
                "-v",
                "0",
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

    if res.returncode > 0:
        print(res.stderr.decode())

    return int(float(res.stdout.decode()))


def get_audio_params(path: str) -> AudioParameters:
    res = run(
        " ".join(
            [
                "ffprobe",
                "-v",
                "0",
                "-select_streams",
                "a:0",
                "-show_entries",
                "stream=sample_rate,channels",
                "-of",
                "compact=p=0:nk=1:s=x",
                f'"{path}"',
            ]
        ),
        shell=True,
        stdout=PIPE,
        stderr=PIPE,
    )

    if res.returncode > 0:
        print(res.stderr.decode())

    out_split = res.stdout.decode().split("x")
    return AudioParameters(
        int(out_split[0]),
        channels=int(out_split[1]),
    )


def get_resolution(path: str) -> VideoParameters:
    res = run(
        " ".join(
            [
                "ffprobe",
                "-v",
                "0",
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

    if res.returncode > 0:
        print(res.stderr.decode())

    out_split = res.stdout.decode().split("x")

    if len(out_split) > 2:
        rate_split = out_split[2].split("/")

        rate_parsed = __parse_int(rate_split[0]) // __parse_int(rate_split[1])
    else:
        rate_parsed = 20

    return VideoParameters(
        width=int(out_split[0]),
        height=int(out_split[1]),
        frame_rate=rate_parsed,
    )

def __parse_int(item: str):
    item = item.strip()

    if not len(item):
        return 1

    if "\n" in item:
        return int(item[item.find("\n") + 1 :])

    return int(item)
