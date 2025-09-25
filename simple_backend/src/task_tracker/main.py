from fastapi import FastAPI, status, HTTPException
from enum import Enum
from pydantic import BaseModel

app = FastAPI()

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
    title: str | None
    status: TaskStatus | None

tasks: dict[int, Task] = {}

_next_id = 1

@app.get("/tasks", response_model=list[Task])
def get_tasks() -> list[Task]:
    return list(tasks.values())

@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> Task:
    global _next_id
    new_task = Task(id=_next_id, **payload.model_dump())
    tasks[_next_id] = new_task
    _next_id += 1
    return new_task

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Задача не найдена!")

    stored_task = tasks[task_id]

    update_data = payload.model_dump(exclude_unset=True)
    updated_task = stored_task.model_copy(update=update_data)

    tasks[task_id] = updated_task
    return updated_task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> None:
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Задача не найдена!")
    tasks.pop(task_id)
    return None

