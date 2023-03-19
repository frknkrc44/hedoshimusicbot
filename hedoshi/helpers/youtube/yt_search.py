from requests import get
from typing import Optional
from urllib.parse import quote_plus
from time import sleep
from json import loads


def search_query(query: str) -> Optional[str]:
    "Returns link if query is valid"

    if not query or not len(query):
        return None

    url = f'https://www.youtube.com/results?search_query={quote_plus(query)}'

    def send_query():
        return get(url, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'SEC-FETCH-DEST': 'document',
            'SEC-FETCH-MODE': 'navigate',
            'SEC-FETCH-SITE': 'none',
            'SEC-FETCH-USER': '?1',
            'UPGRADE-INSECURE-REQUESTS': '1',
        })

    tag = 'ytInitialData'

    while not tag in (res := send_query()).text:
        sleep(1)

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
