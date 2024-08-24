# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from json import loads
from os.path import exists
from time import sleep
from typing import Optional, Tuple
from urllib.parse import quote_plus

from httpx import AsyncClient
from pyrogram.types import Message

from ..pre_query import insert_pre_query, remove_pre_query
from ..spotify import spotify_get_track_info
from .invidious import search_invidious
from yt_dlp.cookies import YoutubeDLCookieJar


async def search_from_spotify_link(source: Message, url: str) -> Optional[str]:
    if insert_pre_query(
        source.chat.id,
        url,
        source.from_user.id if source.from_user else source.chat.id,
    ):
        return None

    track_info: Tuple = await spotify_get_track_info(url)

    remove_pre_query(
        source.chat.id,
        url,
        source.from_user.id if source.from_user else source.chat.id,
    )

    if track_info:
        return await search_query(source, " ".join(track_info))


async def search_query(source: Message, query: str) -> Optional[str]:
    "Returns link if query is valid"

    if not query or not len(query):
        return None

    if insert_pre_query(
        source.chat.id,
        query,
        source.from_user.id if source.from_user else source.chat.id,
    ):
        return None

    from ... import bot_config

    use_invidious = (
        bot_config.BOT_USE_INVIDIOUS
        if hasattr(bot_config, "BOT_USE_INVIDIOUS")
        else False
    )

    if use_invidious:
        result = await search_invidious(query)
        if result:
            remove_pre_query(
                source.chat.id,
                query,
                source.from_user.id if source.from_user else source.chat.id,
            )
            return result

    url = f'https://www.youtube.com/results?search_query={quote_plus(query)}'

    ytdl_cookie_file = (
        bot_config.YTDL_COOKIE_FILE if hasattr(bot_config, "YTDL_COOKIE_FILE") else None
    )

    cookie_content: Optional[str] = None
    if ytdl_cookie_file and exists(ytdl_cookie_file):
        jar = YoutubeDLCookieJar()
        jar.load(ytdl_cookie_file)

        cookie_content = jar.get_cookie_header(url)

    async def send_query():
        try:
            async with AsyncClient() as http:
                headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
                    "SEC-FETCH-DEST": "document",
                    "SEC-FETCH-MODE": "navigate",
                    "SEC-FETCH-SITE": "none",
                    "SEC-FETCH-USER": "?1",
                    "UPGRADE-INSECURE-REQUESTS": "1",
                }

                if cookie_content:
                    headers["Cookie"] = cookie_content

                return await http.get(
                    url,
                    headers=headers,
                )
        except BaseException:
            return None

    tag = 'ytInitialData'

    while tag not in (res := await send_query()).text:
        sleep(1)

    remove_pre_query(
        source.chat.id,
        query,
        source.from_user.id if source.from_user else source.chat.id,
    )

    start = res.text.index(tag) + len(tag) + 3
    end = res.text.index('};', start) + 1
    json = loads(res.text[start:end])
    for contents in json["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"]:
        for video in contents["itemSectionRenderer"]["contents"]:
            if "videoRenderer" in video.keys():
                video_data = video.get("videoRenderer", {})
                id = video_data.get("videoId", None)
                if id and len(id):
                    return f'https://www.youtube.com/watch?v={id}'

    return None
