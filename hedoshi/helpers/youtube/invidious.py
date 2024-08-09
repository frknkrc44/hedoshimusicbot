from httpx import AsyncClient, URL
from yt_dlp.extractor.lazy_extractors import YoutubeIE
from os import getcwd, remove, sep
from os.path import exists
from random import shuffle
from re import match
from typing import List, Optional


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


async def __youtube2invidious(url: str, audio: bool):
    if match(YoutubeIE._VALID_URL, url):
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
                            formats = out_json["adaptiveFormats"]
                            last_audio = None

                            for item in formats:
                                if "audioQuality" in item:
                                    last_audio = item
                                else:
                                    break

                            container = last_audio["container"]
                            if container == "webm":
                                container = "opus"

                            return (
                                out_json["title"],
                                out_json["author"],
                                last_audio["url"],
                                container,
                            )
                        else:
                            streams = out_json["formatStreams"]
                            if len(streams):
                                last_stream = streams[-1]
                                return (
                                    out_json["title"],
                                    out_json["author"],
                                    last_stream["url"],
                                    last_stream["container"],
                                )
                    else:
                        try_count = try_count + 1
            except BaseException:
                try_count = try_count + 1

    return None


async def download_from_invidious(url: str, audio: bool) -> Optional[str]:
    result = await __youtube2invidious(url, audio)

    if result:
        title, author, media, ext = result
    else:
        return None

    file_name = (
        f"{getcwd()}{sep}downloads{sep}{author}-{title}-{'a' if audio else 'v'}.{ext}"
    )

    if exists(file_name):
        return file_name

    async with AsyncClient() as http:
        output = open(file_name, "wb")

        async with http.stream(
            "GET",
            URL(media),
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0 Win64 x64 rv:109.0) Gecko/20100101 Firefox/113.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "tr,en-USq=0.7,enq=0.3",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Sec-GPC": "1",
                "Priority": "u=1",
            },
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
