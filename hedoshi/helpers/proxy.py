from logging import info
from requests import get
from random import shuffle


def get_proxy() -> str:
    proxy_dl_urls = [
        "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/https.txt",
        "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/https.txt",
        "https://raw.githubusercontent.com/zloi-user/hideip.me/main/https.txt",
        "https://raw.githubusercontent.com/0x1337fy/fresh-proxy-list/archive/storage/classic/https.txt",
        "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/http.txt",
        "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt",
    ]

    for url in proxy_dl_urls:
        try:
            req = get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0 Win64 x64 rv:109.0) Gecko/20100101 Firefox/113.0",
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Language": "tr,en-USq=0.7,enq=0.3",
                    "Referer": "https://github.com/",
                    "Origin": "https://github.com",
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

                info(f"Trying {item}")

                try:
                    req2 = get(
                        "https://www.youtube.com",
                        timeout=1,
                        proxies={
                            "https": item,
                            "http": item,
                        },
                    )
                    info(f"Status code: {req2.status_code}")

                    if req2.status_code == 200:
                        return item
                except BaseException:
                    continue

        except BaseException:
            pass

    raise Exception
