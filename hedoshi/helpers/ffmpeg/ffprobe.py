# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from subprocess import PIPE, run
from typing import List, Optional

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

    return __parse_fint(res.stdout.decode(), 0)


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
        bitrate=__parse_int(__get_item(out_split, 0), 44100),
        channels=__parse_int(__get_item(out_split, 1), 2),
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

        rate_parsed = __parse_int(rate_split[0], 20) // __parse_int(rate_split[1], 1)
    else:
        rate_parsed = 20

    return VideoParameters(
        width=__parse_int(__get_item(out_split, 0), 960),
        height=__parse_int(__get_item(out_split, 1), 540),
        frame_rate=rate_parsed,
    )


def __get_item(items: List, idx: int):
    if not items or len(items) <= idx:
        return None

    return items[idx]


def __parse_fint(item: str, default: int = 0):
    try:
        item = item.strip()

        if not len(item):
            return default

        if "\n" in item:
            item = item[item.find("\n") + 1 :]

        return int(float(item))
    except BaseException:
        return default


def __parse_int(item: str, default: int = 0):
    try:
        item = item.strip()

        if not len(item):
            return default

        if "\n" in item:
            item = item[item.find("\n") + 1 :]

        return int(item)
    except BaseException:
        return default
