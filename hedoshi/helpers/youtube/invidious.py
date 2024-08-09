# Copyright (C) 2023 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from httpx import AsyncClient, URL
from yt_dlp.extractor.lazy_extractors import YoutubeIE
from os import getcwd, remove, sep
from os.path import exists
from random import shuffle
from re import match
from traceback import format_exc
from typing import Dict, List, Optional, Tuple
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
            if uri not in tried_instances:
                return uri

    return None


def is_valid_invidious_match(url: str):
    return match(YoutubeIE._VALID_URL, url)


async def __youtube2invidious(url: str, audio: bool):
    if is_valid_invidious_match(url):
        print("Valid match")
        try_count = 0

        tried_instances = []
        while try_count < 10:
            mirror = await __get_valid_invidious_mirror(tried_instances)
            tried_instances.append(mirror)

            print("Selected invidious instance:", mirror)

            video_id = None

            if "watch?v=" in url:
                video_id = url[url.find("=") + 1 :]
                find_and = video_id.find("&")

                if find_and >= 0:
                    video_id = video_id[:find_and]

            videos_url = f"{mirror}/api/v1/videos/{video_id}"

            try:
                async with AsyncClient() as http:
                    req = await http.get(videos_url)
                    out_json = req.json()
                    if "error" not in out_json:
                        if audio:
                            audio_url, container = __get_audio_url(out_json)

                            return (
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
                                out_json["title"],
                                out_json["author"],
                                None,
                                audio_video_url,
                                container,
                            )
                        else:
                            audio_url, _ = __get_audio_url(out_json)
                            video_url, container = __get_video_url(out_json)

                            return (
                                out_json["title"],
                                out_json["author"],
                                audio_url,
                                video_url,
                                container,
                            )
                    else:
                        try_count = try_count + 1
            except BaseException:
                print(format_exc())
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

    container = last_audio["container"]
    if container == "webm":
        container = "opus"

    return last_audio["url"], container


def __get_video_url(out_json: Dict) -> Optional[Tuple[str, str]]:
    formats = out_json["adaptiveFormats"]
    last_video = None

    for item in formats:
        if "audioQuality" in item:
            continue
        else:
            last_video = item

    if "container" not in last_video:
        file_type: str = last_video["type"]
        last_video["container"] = file_type[
            file_type.find("/") + 1 : file_type.find(";")
        ]

    return last_video["url"], last_video["container"]


def __get_audio_video_url(out_json: Dict) -> Optional[Tuple[str, str]]:
    streams = out_json["formatStreams"]

    if len(streams):
        last_stream = streams[-1]
        return last_stream["url"], last_stream["container"]

    return None


async def download_from_invidious(url: str, audio: bool) -> Optional[str]:
    result = await __youtube2invidious(url, audio)

    if result:
        title, author, audio_url, video_url, ext = result
    else:
        return None

    file_name = (
        f"{getcwd()}{sep}downloads{sep}{author}-{title}-{'a' if audio else 'v'}.{ext}"
    )

    if exists(file_name):
        return file_name

    if not audio_url and video_url:
        video_file = await __async_file_download(
            video_url,
            f"{file_name}",
        )

        return video_file

    audio_file = await __async_file_download(
        audio_url,
        f"{file_name}-aud" if video_url else file_name,
    )

    if not audio_file:
        return None

    if video_url:
        video_file = await __async_file_download(
            video_url,
            f"{file_name}-vid",
        )

        if not video_file:
            return None

        if await merge_files(audio_file, video_file, file_name):
            remove(audio_file)
            remove(video_file)

            return file_name
    else:
        return audio_file

    return None


async def __async_file_download(url: str, file_name: str) -> Optional[str]:
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

    async with AsyncClient() as http:
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

            val = await stream.aread()
            output.write(val)
            output.close()
            print("Download finished!")

            return file_name
