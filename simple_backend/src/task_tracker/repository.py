import json
from pathlib import Path
from models import Task
from pydantic import BaseModel

DATA_FILE = Path("tasks.json")

class TaskRepository:
    def __init__(self, path: Path = DATA_FILE):
        self.path = path
        self.tasks: dict[int, Task] = {}
        self.next_id: int = 1
        self.load()

    def load(self) -> None:
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self.tasks = {int(k): Task(**v) for k, v in data.get("tasks", {}).items()}
            self.next_id = int(data.get("next_id", 1))
        else:
            self.tasks, self.next_id = {}, 1

    def save(self):
        data = {
            "tasks": {k: v.model_dump() for k, v in self.tasks.items()},
            "next_id": self.next_id,
        }
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

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
