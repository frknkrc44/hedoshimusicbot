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
