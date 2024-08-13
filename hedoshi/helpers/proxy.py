# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from httpx import AsyncClient
from logging import info
from random import shuffle


async def get_proxy() -> str:
    from ..bot_config import working_proxies

    try_count = 0
    while try_count < 3:
        shuffle(working_proxies)

        for item in working_proxies:
            if not item.startswith("http"):
                item = f"http://{item}"

            if item.count(":") > 2:
                item = item[: item.rfind(":")]

            try:
                async with AsyncClient(
                    proxy=item,
                    timeout=0.5,
                ) as http:
                    req2 = await http.get(
                        "https://goo.gl",
                        follow_redirects=False,
                    )

                    if req2.status_code < 400:
                        return item
            except BaseException:
                continue

        info("The proxy list is invalid, refreshing...")
        await load_working_proxies()
        try_count = try_count + 1


async def load_working_proxies():
    from ..bot_config import working_proxies

    working_proxies.clear()

    proxy_dl_urls = [
        "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/https.txt",
        "https://raw.githubusercontent.com/zloi-user/hideip.me/main/https.txt",
        "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/https.txt",
    ]

    for url in proxy_dl_urls:
        if len(working_proxies) > 2:
            break

        info(f"Trying {url}")

        try:
            lines = []

            async with AsyncClient() as proxy_list_getter:
                req = await proxy_list_getter.get(
                    url,
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
                )

                lines = req.text.splitlines()

            shuffle(lines)

            for item in lines:
                if not item.startswith("http"):
                    item = f"http://{item}"

                if item.count(":") > 2:
                    item = item[: item.rfind(":")]

                try:
                    async with AsyncClient(
                        proxy=item,
                        timeout=0.5,
                    ) as http:
                        req2 = await http.get(
                            "https://goo.gl",
                            follow_redirects=False,
                        )

                        if req2.status_code < 400:
                            print(f"Found {item}")
                            working_proxies.append(item)
                except BaseException:
                    pass

                if len(working_proxies) > 2:
                    break
        except BaseException:
            pass
