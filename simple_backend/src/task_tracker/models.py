from enum import Enum
from pydantic import BaseModel

class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class Task(BaseModel):
    id: int
    title: str
    status: TaskStatus = TaskStatus.todo


class TaskCreate(BaseModel):
    title: str
    status: TaskStatus = TaskStatus.todo


class TaskUpdate(BaseModel):
    title: str | None = None
    status: TaskStatus | None = None