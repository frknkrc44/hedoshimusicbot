# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from asyncio import get_event_loop, run as async_run
from logging import info
from typing import Dict, Optional, Tuple
from pyrogram.types import Message
from yt_dlp import YoutubeDL
from yt_dlp.postprocessor.common import PostProcessor
import yt_dlp.extractor.extractors as ex
from yt_dlp.extractor.unsupported import KnownDRMIE, KnownPiracyIE
from os import getcwd, sep
from os.path import basename
from re import match
from traceback import format_exc
from ..proxy import get_proxy
from .invidious import download_from_invidious, is_valid_invidious_match
from ..telegram.downloader import _progress_func_wrapper

yt_valid_ends = [
    '.m3u8'
]


class FilenameCollectorPP(PostProcessor):
    # https://stackoverflow.com/a/68165682
    def __init__(self):
        super(FilenameCollectorPP, self).__init__(None)
        self.filenames = []

    def run(self, information):
        self.filenames.append(information['filepath'])
        return [], information


def _is_valid_ends(url: str):
    for item in yt_valid_ends:
        if item in url:
            return True

    return False


def is_in_blacklist(url: str):
    for rule in KnownDRMIE.URLS:
        if match(f".*{rule}.*", url):
            return True

    for rule in KnownPiracyIE.URLS:
        if match(f".*{rule}.*", url):
            return True

    return False


def is_valid(url: str):
    if not url or not url.startswith("http"):
        return False

    for item in ex._ALL_CLASSES:
        try:
            if hasattr(item, '_VALID_URL') and match(getattr(item, '_VALID_URL'), url):
                return True
        except BaseException:
            pass

    return _is_valid_ends(url)


async def download_media(
    reply: Message,
    url: str,
    audio: bool = False,
) -> Optional[Tuple[str, str]]:
    if is_in_blacklist(url):
        return None

    async def invidious_progress_hook(current: int, total: int):
        await _progress_func_wrapper(
            reply,
            current,
            total,
        )

    def ytdl_progress_hook(progress: Dict):
        downloaded = progress.get("downloaded_bytes", 0)
        total = progress.get("total_bytes", max(downloaded, 1))

        async_run(
            invidious_progress_hook(
                downloaded,
                total or max(downloaded, 1),
            )
        )

    from ... import bot_config

    use_invidious = (
        bot_config.BOT_USE_INVIDIOUS
        if hasattr(bot_config, "BOT_USE_INVIDIOUS")
        else False
    )

    use_proxy = (
        bot_config.BOT_USE_PROXY if hasattr(bot_config, "BOT_USE_PROXY") else False
    )

    if use_invidious and is_valid_invidious_match(url):
        try_count = 0
        while try_count < 10:
            try:
                proxy: Optional[str] = None
                if use_proxy:
                    proxy = await get_proxy()

                try_invidious = await download_from_invidious(
                    url,
                    audio,
                    invidious_progress_hook,
                    proxy,
                )

                if try_invidious:
                    return try_invidious

                try_count = try_count + 1
            except BaseException:
                print(format_exc())
                try_count = try_count + 1

    opts = {
        "ignoreerrors": True,
        "outtmpl": f'{getcwd()}{sep}downloads{sep}%(uploader)s-%(title)s-{"a" if audio else "v"}.%(ext)s',
        "cachedir": f"{getcwd()}{sep}downloads",
        "progress_hooks": [ytdl_progress_hook],
    }

    if audio:
        opts['format'] = 'm4a' if 'youtube' in url else 'bestaudio/worstvideo/source'
    else:
        opts["format"] = "bestvideo[height<=1080]+bestaudio/best/source"

    filename_collector = FilenameCollectorPP()
    with YoutubeDL(opts) as ytdl:
        ytdl.add_post_processor(filename_collector)

        try_count = 0
        while try_count < 4:
            try:
                if use_proxy and try_count < 3:
                    ytdl.cookiejar.clear()

                    proxy = await get_proxy()
                    ytdl.proxies = {
                        "https": proxy,
                        "http": proxy,
                    }
                    info(f"Set a random proxy {ytdl.proxies}")

                assert not await get_event_loop().run_in_executor(
                    None,
                    ytdl.download,
                    [url],
                )
            except BaseException:
                try_count = try_count + 1
                continue

            break

    return (
        (filename_collector.filenames[-1], basename(filename_collector.filenames[-1]))
        if len(filename_collector.filenames)
        else None
    )
