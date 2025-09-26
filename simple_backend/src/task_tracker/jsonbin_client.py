import os
from typing import Any
from http_client import BaseHTTPClient


class JsonBinClient(BaseHTTPClient):
    def __init__(self):
        self._api_key = os.environ.get("JSONBIN_API_KEY")
        self._bin_id = os.environ.get("JSONBIN_BIN_ID")
        self._base = os.environ.get("JSONBIN_BASE_URL", "https://api.jsonbin.io/v3")
        self._access = os.environ.get("JSONBIN_ACCESS_KEY")
        if not self._api_key or not self._bin_id:
            raise RuntimeError("JSONBIN_API_KEY и JSONBIN_BIN_ID обязательны")
        super().__init__(timeout=10.0)

    @property
    def base_url(self) -> str:
        return self._base

    @property
    def default_headers(self):
        h = {"X-Master-Key": self._api_key, "Content-Type": "application/json"}
        if self._access:
            h["X-Access-Key"] = self._access
        return h

    def read_latest(self) -> dict[str, Any]:
        data = self.get_json(f"/b/{self._bin_id}/latest")
        return data.get("record") or {}

    def write(self, record: dict[str, Any]) -> dict[str, Any]:
        return self.put_json(f"/b/{self._bin_id}", record)
