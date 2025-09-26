from fastapi import FastAPI, status, HTTPException
from repository import TaskRepository
from models import Task, TaskCreate, TaskUpdate
from cloud_repository import JsonBinRepository
import os
from dotenv import load_dotenv
from llm_client import CloudflareLLM
from logging_config import setup_logging
import logging

logger = logging.getLogger("../task_tracker/main.py")

app = FastAPI()
load_dotenv()
setup_logging()


def get_repo():
    storage = os.environ.get("STORAGE", "file").lower()
    if storage == "jsonbin":
        return JsonBinRepository()
    return TaskRepository()


repo = get_repo()
llm = CloudflareLLM()


@app.get("/tasks", response_model=list[Task])
def get_tasks() -> list[Task]:
    return repo.get_all()


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate) -> Task:
    logger.info(
        "Create task request: title=%r status=%s", payload.title, payload.status
    )
    task = repo.add(title=payload.title, status=payload.status)
    try:
        explanation = await llm.explain_task(task.title)
        task = repo.update(task.id, {"description": explanation})
        logger.info("Task %s enriched by LLM", task.id)
    except Exception:
        logger.exception("LLM enrichment failed for task_id=%s", task.id)
    return task


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
