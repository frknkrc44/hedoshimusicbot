# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from httpx import AsyncClient
from re import match
from typing import Optional, Tuple


def is_spotify_track(url: str):
    return match(r".*open\.spotify\.com/(?:.*)track/.*", url)


async def spotify_get_track_info(url: str) -> Optional[Tuple[str, str]]:
    if not is_spotify_track(url):
        return None

    async with AsyncClient() as http:
        temp_token_result = await http.get("https://open.spotify.com/get_access_token")
        if temp_token_result.status_code >= 400:
            return None

        access_token = temp_token_result.json()["accessToken"]

        track_id = url[url.rfind("/") + 1 :]
        param_symbol = track_id.find("?")
        if param_symbol >= 0:
            track_id = track_id[:param_symbol]

        track_info_result = await http.get(
            f"https://api.spotify.com/v1/tracks/{track_id}?access_token={access_token}"
        )

        if track_info_result.status_code >= 400:
            return None

        result_json = track_info_result.json()

        return (
            result_json["album"]["artists"][0]["name"],
            result_json["name"],
        )
