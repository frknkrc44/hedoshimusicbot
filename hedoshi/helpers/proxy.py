from logging import info
from requests import get
from random import shuffle


def get_proxy() -> str:
    proxy_dl_urls = [
        "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/https.txt",
        "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/https.txt",
        "https://raw.githubusercontent.com/zloi-user/hideip.me/main/https.txt",
    ]
    shuffle(proxy_dl_urls)

    for url in proxy_dl_urls:
        info(f"Trying {url}")

        try:
            req = get(
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
                    req2 = get(
                        "https://1.1.1.1/help/",
                        timeout=1,
                        allow_redirects=False,
                        proxies={
                            "https": item,
                            "http": item,
                        },
                    )

                    if req2.status_code < 400:
                        return item
                except BaseException:
                    continue

        except BaseException:
            pass

    raise Exception
