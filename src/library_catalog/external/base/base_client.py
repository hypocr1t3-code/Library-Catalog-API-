from abc import ABC, abstractmethod
import httpx
import logging
import time

class BaseClient(ABC):
    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        retries: int = 3,
        backoff: float = 0.5,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self._client = httpx.AsyncClient(timeout=self.timeout)
        self.logger = logging.getLogger(self.client_name())

    @abstractmethod
    def client_name(self) -> str:
        """Имя клиента для логирования."""
        ...

    def _build_url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url + path

    async def _request(self, method, path, params=None, json=None, headers=None) -> dict:
        url = self._build_url(path)

        for attempt in range(self.retries):
            try:
                self.logger.debug(f"{method} {url} params={params}")
                response = await self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    headers=headers,
                )
                response.raise_for_status()
                return response.json()

            except httpx.TimeoutException:
                if attempt == self.retries - 1:
                    self.logger.error(f"Timeout after {self.retries} attempts")
                    raise
                wait_time = self.backoff * (2 ** attempt)
                self.logger.warning(f"Timeout, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500 and attempt < self.retries - 1:
                    wait_time = self.backoff * (2 ** attempt)
                    self.logger.warning(f"Server error, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"HTTP error: {e}")
                    raise

            except httpx.RequestError as e:
                if attempt == self.retries - 1:
                    self.logger.error(f"Request error: {e}")
                    raise
                wait_time = self.backoff * (2 ** attempt)
                self.logger.warning(f"Request error, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

        raise RuntimeError("All retries exhausted")

    async def _get(self, path: str, **kwargs) -> dict:
        return await self._request("GET", path, **kwargs)

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

