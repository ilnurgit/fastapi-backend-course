import os, httpx

class CloudflareLLM:
    def __init__(self):
        self.account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
        self.api_key    = os.environ.get("CLOUDFLARE_API_KEY")
        self.model      = os.environ.get("CLOUDFLARE_MODEL", "@cf/meta/llama-2-7b-chat-int8")
        if not self.account_id or not self.api_key:
            raise RuntimeError("CLOUDFLARE_ACCOUNT_ID и CLOUDFLARE_API_KEY обязательны")
        self.url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{self.model}"

    async def explain_task(self, text: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "messages": [
                {"role": "system", "content": "Ты помощник, который предлагает пошаговое решение данной задачи кратко, не более 100 символов на русском языке. В формате, пример: 1 шаг: найти информацию в интернете. 2 шаг: выписать важные моменты"},
                {"role": "user", "content": text},
            ]
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(self.url, headers=headers, json=payload)
            # временно оставим понятную ошибку в логах
            if resp.status_code == 404:
                raise RuntimeError(f"Cloudflare 404: проверь ACCOUNT_ID/модель: url={self.url}")
            resp.raise_for_status()
            data = resp.json()
            # ответ у Workers AI приходит в data["result"]["response"]
            return data["result"]["response"]