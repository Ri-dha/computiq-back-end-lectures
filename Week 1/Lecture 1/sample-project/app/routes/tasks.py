"""PRESENTATION LAYER (slide 2.9)

Requests in, responses out. This is the only layer that knows about HTTP:
methods (GET/POST/PUT/DELETE) and status codes (200/201/204/404/400).

Each function below is one row of the request-methods table from slide 2.6.
"""

from fastapi import APIRouter, HTTPException

from app.models.task import Task, TaskCreate
from app.services import task_service

# A router is just a group of related endpoints that we plug into the app.
router = APIRouter(prefix="/tasks", tags=["tasks"])


# READ ALL  ->  GET /tasks  ->  200 OK
@router.get("", response_model=list[Task])
def list_tasks():
    return task_service.list_tasks()


# READ ONE  ->  GET /tasks/1  ->  200 OK, or 404 Not Found
@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int):
    task = task_service.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# CREATE  ->  POST /tasks  ->  201 Created
@router.post("", response_model=Task, status_code=201)
def create_task(payload: TaskCreate):
    try:
        return task_service.create_task(payload.title, payload.done)
    except ValueError as error:
        # A rule from the service layer was broken -> that's a client error.
        raise HTTPException(status_code=400, detail=str(error))


# UPDATE  ->  PUT /tasks/1  ->  200 OK, or 404 Not Found
@router.put("/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskCreate):
    try:
        task = task_service.update_task(task_id, payload.title, payload.done)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# DELETE  ->  DELETE /tasks/1  ->  204 No Content, or 404 Not Found
@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int):
    if not task_service.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    # 204 means "success, and there is deliberately nothing to send back".
    return None
