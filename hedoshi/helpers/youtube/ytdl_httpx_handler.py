from asyncio import run
from io import IOBase
from traceback import format_exception
from typing import AsyncIterator, Dict, Optional

from httpx import AsyncClient, Request, Response
from yt_dlp.networking.common import Features
from yt_dlp.networking.common import Request as YtDLRequest
from yt_dlp.networking.common import RequestHandler
from yt_dlp.networking.common import Response as YtDLResponse


class HTTPXRH(RequestHandler):
    _SUPPORTED_URL_SCHEMES = ("http", "https", "data", "ftp")
    _SUPPORTED_PROXY_SCHEMES = ("http", "socks4", "socks4a", "socks5", "socks5h")
    _SUPPORTED_FEATURES = (Features.NO_PROXY, Features.ALL_PROXY)
    RH_NAME = "httpx"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _send(self, request: YtDLRequest) -> YtDLResponse:
        return run(self._asend(request))

    def _get_proxies(self, request) -> Optional[Dict]:
        proxies = super()._get_proxies(request)

        if not proxies:
            return None

        return {f"{k}://": v for k, v in proxies.items()}

    async def _asend(self, request: YtDLRequest) -> YtDLResponse:
        proxies: dict = self._get_proxies(request)

        async with AsyncClient(
            proxies=proxies,
            timeout=30,
        ) as http:
            sent = await http.send(
                Request(
                    request.method,
                    request.url,
                    headers=request.headers,
                    data=request.data,
                ),
                follow_redirects=True,
            )

            return HttpXResponse(sent)


class _HTTPXByteStream(IOBase):
    def __init__(self, response: Response) -> None:
        self.response = response
        self.reader: AsyncIterator[bytes] = None

    def read(self, chunk_size: int) -> bytes:
        if self.reader is None:
            self.reader = self.response.aiter_bytes(chunk_size)

        try:
            return run(self.reader.__anext__())
        except BaseException as e:
            print("\n".join(format_exception(e)))
            raise e

    def _checkClosed(self) -> None:
        if self.reader is not None and self.response.is_closed:
            raise ValueError("The connection is closed")

    def close(self) -> None:
        return self.response.close()


class HttpXResponse(YtDLResponse):
    def __init__(
        self,
        response: Response,
    ):
        super().__init__(
            _HTTPXByteStream(response),
            response.url,
            response.headers,
            response.status_code,
            response.reason_phrase,
        )
