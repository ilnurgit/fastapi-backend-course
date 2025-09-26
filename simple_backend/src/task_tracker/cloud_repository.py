from models import Task
from jsonbin_client import JsonBinClient


class JsonBinRepository:
    """
    Хранит задачи в jsonbin.io. Формат:
    {"next_id": int, "tasks": { "<id>": { ...Task... } } }
    """

    def __init__(self, client: JsonBinClient | None = None):
        self.client = client or JsonBinClient()
        self.tasks: dict[int, Task] = {}
        self.next_id: int = 1
        self.load()

    def load(self) -> None:
        data = self.client.read_latest()
        tasks_raw = data.get("tasks", {})
        self.tasks = {int(k): Task(**v) for k, v in tasks_raw.items()}
        self.next_id = int(data.get("next_id", 1))

    def save(self) -> None:
        body = {
            "tasks": {k: v.model_dump() for k, v in self.tasks.items()},
            "next_id": self.next_id,
        }
        self.client.write(body)

    def get_all(self) -> list[Task]:
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
