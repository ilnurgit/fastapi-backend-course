from fastapi import FastAPI, status, HTTPException
from repository import TaskRepository
from models import Task, TaskStatus, TaskCreate, TaskUpdate
from cloud_repository import JsonBinRepository
import os
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()

def get_repo():
    storage = os.environ.get("STORAGE", "file").lower()
    if storage == "jsonbin":
        return JsonBinRepository()
    return TaskRepository()

repo = get_repo()

@app.get("/tasks", response_model=list[Task])
def get_tasks() -> list[Task]:
    return repo.get_all()


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> Task:
    return repo.add(title=payload.title, status=payload.status)


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate):
    if task_id not in repo.tasks:
        raise HTTPException(status_code=404, detail="Задача не найдена!")
    patch = payload.model_dump(exclude_none=True, exclude_unset=True)
    return repo.update(task_id, patch)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> None:
    if task_id not in repo.tasks:
        raise HTTPException(status_code=404, detail="Задача не найдена!")
    repo.delete(task_id)
    return None
