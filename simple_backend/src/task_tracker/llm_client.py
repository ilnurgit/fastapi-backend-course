import os
from http_client import AsyncBaseHTTPClient


class CloudflareLLM(AsyncBaseHTTPClient):
    def __init__(self):
        self.account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
        self.api_key = os.environ.get("CLOUDFLARE_API_KEY")
        self.model = os.environ.get("CLOUDFLARE_MODEL", "@cf/meta/llama-3-8b-instruct")
        if not self.account_id or not self.api_key:
            raise RuntimeError("CLOUDFLARE_ACCOUNT_ID и CLOUDFLARE_API_KEY обязательны")
        super().__init__(timeout=30.0)

    @property
    def base_url(self) -> str:
        return f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run"

    @property
    def default_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def explain_task(self, text: str) -> str:
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Ты помощник, который предлагает пошаговое решение задачи кратко "
                        "(<100 символов на шаг), по-русски. Формат: 1) ... 2) ..."
                    ),
                },
                {"role": "user", "content": text},
            ]
        }
        path = "/" + self.model.lstrip("/")
        data = await self.post_json(path, payload)
        return data["result"]["response"]
