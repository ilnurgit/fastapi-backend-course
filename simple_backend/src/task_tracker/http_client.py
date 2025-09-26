from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Mapping
import logging
import httpx

logger = logging.getLogger("task_tracker.http")


# ----- СИНХРОННЫЙ БАЗОВЫЙ КЛИЕНТ -----
class BaseHTTPClient(ABC):
    def __init__(self, *, timeout: float = 10.0):
        self._client = httpx.Client(timeout=timeout)

    @property
    @abstractmethod
    def base_url(self) -> str: ...

    @property
    @abstractmethod
    def default_headers(self) -> Mapping[str, str]: ...

    def _join(self, path: str) -> str:
        if path.startswith("/"):
            path = path[1:]
        return f"{self.base_url.rstrip('/')}/{path}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Any | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        url = self._join(path)
        merged = {**self.default_headers, **(headers or {})}
        try:
            resp = self._client.request(method, url, headers=merged, json=json)
        except httpx.HTTPError as e:
            logger.exception("Network error %s %s: %s", method, url, e)
            raise
        if resp.status_code >= 400:
            logger.error(
                "HTTP %s for %s %s: %s",
                resp.status_code,
                method,
                url,
                (resp.text or "")[:300],
            )
            resp.raise_for_status()
        return resp

    def get_json(self, path: str) -> Any:
        return self._request("GET", path).json()

    def put_json(self, path: str, payload: Any) -> Any:
        return self._request("PUT", path, json=payload).json()

    def post_json(self, path: str, payload: Any) -> Any:
        return self._request("POST", path, json=payload).json()


# ----- АСИНХРОННЫЙ БАЗОВЫЙ КЛИЕНТ -----
class AsyncBaseHTTPClient(ABC):
    def __init__(self, *, timeout: float = 30.0):
        self._client = httpx.AsyncClient(timeout=timeout)

    @property
    @abstractmethod
    def base_url(self) -> str: ...

    @property
    @abstractmethod
    def default_headers(self) -> Mapping[str, str]: ...

    def _join(self, path: str) -> str:
        if path.startswith("/"):
            path = path[1:]
        return f"{self.base_url.rstrip('/')}/{path}"

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: Any | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        url = self._join(path)
        merged = {**self.default_headers, **(headers or {})}
        try:
            resp = await self._client.request(method, url, headers=merged, json=json)
        except httpx.HTTPError as e:
            logger.exception("Network error %s %s: %s", method, url, e)
            raise
        if resp.status_code >= 400:
            logger.error(
                "HTTP %s for %s %s: %s",
                resp.status_code,
                method,
                url,
                (resp.text or "")[:300],
            )
            resp.raise_for_status()
        return resp

    async def get_json(self, path: str) -> Any:
        return (await self._request("GET", path)).json()

    async def put_json(self, path: str, payload: Any) -> Any:
        return (await self._request("PUT", path, json=payload)).json()

    async def post_json(self, path: str, payload: Any) -> Any:
        return (await self._request("POST", path, json=payload)).json()
