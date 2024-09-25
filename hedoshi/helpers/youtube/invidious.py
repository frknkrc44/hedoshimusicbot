# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from asyncio import iscoroutinefunction
from os import getcwd, remove, sep
from os.path import exists, getsize
from random import shuffle
from re import match
from typing import Callable, Dict, List, Optional, Tuple

from httpx import URL, AsyncClient
from yt_dlp.extractor.lazy_extractors import YoutubeIE

from ..ffmpeg.ffmpeg import merge_files


async def __get_instances_list() -> List:
    mirrors_url = "https://api.invidious.io/instances.json"

    async with AsyncClient() as http:
        req = await http.get(mirrors_url)
        return req.json()


async def __get_valid_invidious_mirror(tried_instances: List[str]) -> Optional[str]:
    if "instances" not in globals():
        globals()["instances"] = await __get_instances_list()

    instances: List = globals()["instances"]
    shuffle(instances)

    for item in instances:
        _, instance_options = item
        if instance_options.get("api", False) is True:
            uri = instance_options.get("uri")
            playback_ratio = 0.5

            try:
                playback_ratio = (
                    instance_options.get("stats").get("playback").get("ratio")
                )
            except BaseException:
                pass

            if not playback_ratio:
                playback_ratio = 0.5

            if uri not in tried_instances and playback_ratio >= 0.5:
                return uri

    return None


async def search_invidious(query: str) -> str:
    try_count = 0

    tried_instances = []
    while try_count < 10:
        mirror = await __get_valid_invidious_mirror(tried_instances)
        tried_instances.append(mirror)

        if not mirror:
            tried_instances.clear()
            try_count = try_count + 1
            continue

        print("Selected invidious instance:", mirror)

        search_url = f"{mirror}/api/v1/search?q={query}"

        try:
            async with AsyncClient(timeout=10) as http:
                req = await http.get(search_url)
                out_json = req.json()

                if type(out_json) is list:
                    for item in out_json:
                        if item.get("type") == "video":
                            return (
                                f'https://www.youtube.com/watch?v={item.get("videoId")}'
                            )

                try_count = try_count + 1
        except BaseException:
            try_count = try_count + 1

    return None


def is_valid_invidious_match(url: str):
    return match(YoutubeIE._VALID_URL, url)


async def __youtube2invidious(url: str, audio: bool, max_video_quality: int):
    if is_valid_invidious_match(url):
        try_count = 0

        tried_instances = []
        while try_count < 10:
            mirror = await __get_valid_invidious_mirror(tried_instances)
            if not mirror:
                continue

            tried_instances.append(mirror)

            print("Selected invidious instance:", mirror)

            video_id = None

            if "watch?v=" in url:
                video_id = url[url.find("=") + 1 :]
                find_and = video_id.find("&")

                if find_and >= 0:
                    video_id = video_id[:find_and]
            elif "/shorts/" in url or "/youtu.be/" in url:
                video_id = url[url.rfind("/") + 1 :]
                find_qs = video_id.find("?")

                if find_qs >= 0:
                    video_id = video_id[:find_qs]
            else:
                return None

            videos_url = f"{mirror}/api/v1/videos/{video_id}"

            try:
                async with AsyncClient(timeout=5) as http:
                    req = await http.get(videos_url)
                    out_json = req.json()

                    if "error" not in out_json:
                        if audio:
                            audio_url, container = __get_audio_url(out_json)

                            return (
                                video_id,
                                out_json["title"],
                                out_json["author"],
                                audio_url,
                                None,
                                container,
                            )

                        from ... import bot_config

                        use_legacy = (
                            bot_config.BOT_INVIDIOUS_LEGACY_VIDEO
                            if hasattr(bot_config, "BOT_INVIDIOUS_LEGACY_VIDEO")
                            else False
                        )

                        if use_legacy:
                            audio_video_url, container = __get_audio_video_url(out_json)

                            return (
                                video_id,
                                out_json["title"],
                                out_json["author"],
                                None,
                                audio_video_url,
                                container,
                            )
                        else:
                            audio_url, video_url, container = __get_video_url(
                                out_json,
                                max_video_quality,
                            )

                            return (
                                video_id,
                                out_json["title"],
                                out_json["author"],
                                audio_url,
                                video_url,
                                container,
                            )
                    else:
                        try_count = try_count + 1
            except BaseException:
                try_count = try_count + 1

    return None


def __get_audio_url(out_json: Dict) -> Optional[Tuple[str, str]]:
    formats = out_json["adaptiveFormats"]
    last_audio = None

    for item in formats:
        if "audioQuality" in item:
            last_audio = item
        else:
            break

    if "container" not in last_audio:
        file_type: str = last_audio["type"]
        last_audio["container"] = file_type[
            file_type.find("/") + 1 : file_type.find(";")
        ]

    return last_audio["url"], last_audio["container"]


def __get_video_url(
    out_json: Dict,
    max_video_quality: int,
) -> Optional[Tuple[str, str, str]]:
    formats = out_json["adaptiveFormats"]
    last_audio = None
    last_video = None

    for item in formats:
        if "audioQuality" in item:
            last_audio = item
        else:
            last_video = item

            # limit max to max_video_quality
            quality = f"{max_video_quality}p"
            if item.get("resolution") == quality or item.get("qualityLabel") == quality:
                break

    if "container" not in last_video:
        file_type: str = last_video["type"]
        last_video["container"] = file_type[
            file_type.find("/") + 1 : file_type.find(";")
        ]

    return last_audio["url"], last_video["url"], last_video["container"]


def __get_audio_video_url(out_json: Dict) -> Optional[Tuple[str, str]]:
    streams = out_json["formatStreams"]

    if len(streams):
        last_stream = streams[-1]
        return last_stream["url"], last_stream["container"]

    return None


async def download_from_invidious(
    url: str,
    audio: bool,
    progress_hook: Callable[[int, int], None],
    proxy: Optional[str],
    max_video_quality: int = 1080,
) -> Optional[Tuple[str, str]]:
    result = await __youtube2invidious(url, audio, max_video_quality)

    if result:
        video_id, title, author, audio_url, video_url, ext = result
    else:
        return None

    file_name_suffix = f"{author} - {title} ({'a' if audio else 'v'})"
    file_name = f"{getcwd()}{sep}downloads{sep}{video_id}-{'a' if audio else 'v'}.{ext}"

    if exists(file_name):
        return file_name, file_name_suffix

    if not audio_url and video_url:
        video_file = await __async_file_download(
            video_url,
            f"{file_name}",
            progress_hook,
            proxy,
        )

        return video_file, file_name_suffix

    audio_file = await __async_file_download(
        audio_url,
        f"{file_name}-aud" if video_url else file_name,
        progress_hook,
        proxy,
    )

    if not audio_file:
        return None

    if video_url:
        video_file = await __async_file_download(
            video_url,
            f"{file_name}-vid",
            progress_hook,
            proxy,
        )

        if not video_file:
            return None

        if await merge_files(audio_file, video_file, file_name):
            remove(audio_file)
            remove(video_file)

            return file_name, file_name_suffix
    else:
        return audio_file, file_name_suffix

    return None


async def __async_file_download(
    url: str,
    file_name: str,
    progress_hook: Callable[[int, int], None],
    proxy: Optional[str],
) -> Optional[str]:
    if not url:
        return None

    if url and not url.startswith("http"):
        return None

    try_count = 0
    while try_count < 3:
        try:
            http_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0 Win64 x64 rv:109.0) Gecko/20100101 Firefox/113.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "tr,en-USq=0.7,enq=0.3",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Sec-GPC": "1",
                "Priority": "u=1",
            }

            async with AsyncClient(
                proxy=proxy,
                timeout=5,
            ) as http:
                output = open(file_name, "wb")

                async with http.stream(
                    "GET",
                    URL(url),
                    follow_redirects=True,
                    headers=http_headers,
                ) as stream:
                    print("Status:", stream.status_code)
                    if stream.status_code >= 400:
                        output.close()

                        if exists(file_name):
                            remove(file_name)

                        return None

                    total = int(stream.headers.get("Content-Length", 0))
                    async for data in stream.aiter_bytes():
                        output.write(data)

                        if iscoroutinefunction(progress_hook):
                            await progress_hook(
                                stream.num_bytes_downloaded,
                                total,
                            )
                        else:
                            progress_hook(
                                stream.num_bytes_downloaded,
                                total,
                            )

                    output.close()

                    assert exists(file_name) and total == getsize(file_name)

                    print("Download finished!")
                    return file_name
        except BaseException:
            try_count = try_count + 1

            if exists(file_name):
                remove(file_name)

    return None
