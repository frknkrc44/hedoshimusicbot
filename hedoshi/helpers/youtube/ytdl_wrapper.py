# Copyright (C) 2023 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from logging import info
from yt_dlp import YoutubeDL
from yt_dlp.postprocessor.common import PostProcessor
import yt_dlp.extractor.extractors as ex
from os import getcwd, sep
from re import match
from ..proxy import get_proxy

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


def is_valid(url: str):
    if not url.startswith('http'):
        return False

    for item in ex._ALL_CLASSES:
        try:
            if hasattr(item, '_VALID_URL') and match(getattr(item, '_VALID_URL'), url):
                return True
        except BaseException:
            pass

    return _is_valid_ends(url)


def download_media(url: str, audio: bool = False) -> str:
    globals()['last_percent'] = -1
    globals()['last_percent_epoch'] = 0

    opts = {
        'ignoreerrors': True,
        'outtmpl': f'{getcwd()}{sep}downloads{sep}%(uploader)s-%(title)s-{"a" if audio else "v"}.%(ext)s',
        'cachedir': f'{getcwd()}{sep}downloads',
    }

    if audio:
        opts['format'] = 'm4a' if 'youtube' in url else 'bestaudio/worstvideo/source'
    else:
        opts["format"] = "bestvideo+bestaudio/best/source"

    filename_collector = FilenameCollectorPP()
    with YoutubeDL(opts) as ytdl:
        ytdl.add_post_processor(filename_collector)

        try_count = 0
        while try_count < 4:
            try:
                from ... import bot_config

                use_proxy = (
                    bot_config.BOT_USE_PROXY
                    if hasattr(bot_config, "BOT_USE_PROXY")
                    else False
                )
                print(type(use_proxy), use_proxy)

                if use_proxy and try_count < 3:
                    ytdl.proxies = {
                        "https": get_proxy(),
                    }
                    info(f"Set a random proxy {ytdl.proxies}")

                assert not ytdl.download([url])
            except BaseException:
                try_count = try_count + 1
                continue

            break

    return (
        filename_collector.filenames[-1] if len(filename_collector.filenames) else None
    )
