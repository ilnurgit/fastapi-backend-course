import os
import json
import httpx
from models import Task

class JsonBinRepository:
    """
    Хранит задачи в jsonbin.io. Данные лежат в формате:
    {"next_id": int, "tasks": { "<id>": { ...Task... } } }
    """
    def __init__(self,
                 api_key: str | None = None,
                 bin_id: str | None = None,
                 base_url: str | None = None):
        self.api_key = api_key or os.environ.get("JSONBIN_API_KEY")
        self.bin_id = bin_id or os.environ.get("JSONBIN_BIN_ID")
        self.base_url = base_url or os.environ.get("JSONBIN_BASE_URL", "https://api.jsonbin.io/v3")
        if not self.api_key or not self.bin_id:
            raise RuntimeError("JSONBIN_API_KEY и JSONBIN_BIN_ID обязательны")

        self.headers = {
            "X-Master-Key": self.api_key,
            "Content-Type": "application/json",
        }
        self.tasks: dict[int, Task] = {}
        self.next_id: int = 1
        self.load()

    def _bin_read_url(self) -> str:
        # GET для чтения актуальной версии
        return f"{self.base_url}/b/{self.bin_id}/latest"

    def _bin_write_url(self) -> str:
        # PUT для полной замены содержимого
        return f"{self.base_url}/b/{self.bin_id}"

    def load(self) -> None:
        resp = httpx.get(self._bin_read_url(), headers=self.headers, timeout=10.0)
        resp.raise_for_status()
        payload = resp.json()              # {'record': {...}, ...}
        data = payload.get("record") or {} # сам объект, что мы сохраняем

        tasks_raw = data.get("tasks", {})
        self.tasks = {int(k): Task(**v) for k, v in tasks_raw.items()}
        self.next_id = int(data.get("next_id", 1))

    def save(self) -> None:
        body = {
            "tasks": {k: v.model_dump() for k, v in self.tasks.items()},
            "next_id": self.next_id,
        }
        resp = httpx.put(self._bin_write_url(),
                         headers=self.headers,
                         content=json.dumps(body, ensure_ascii=False, indent=2),
                         timeout=10.0)
        resp.raise_for_status()

    # CRUD
    def get_all(self) -> list[Task]:
        # можно перед каждым запросом перечитывать load(), если нужен always-fresh
        return list(self.tasks.values())

    def add(self, title: str, status: str) -> Task:
        t = Task(id=self.next_id, title=title, status=status)
        self.tasks[self.next_id] = t
        self.next_id += 1
        self.save()
        return t

    def update(self, task_id: int, patch: dict) -> Task:
        current = self.tasks[task_id]
        updated = current.model_copy(update=patch)
        self.tasks[task_id] = updated
        self.save()
        return updated

    def delete(self, task_id: int) -> None:
        self.tasks.pop(task_id, None)
        self.save()