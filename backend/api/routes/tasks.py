from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.api.dependencies import get_current_user
from backend.db.models import User
from backend.db.session import get_db
from backend.schemas.task import TaskCreate, TaskRead, TaskUpdate
from backend.services.task import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])
service = TaskService()


@router.get("", response_model=list[TaskRead])
def list_tasks(
    project_id: int | None = Query(default=None, alias="projectId"),
    task_status: str | None = Query(default=None, alias="status"),
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TaskRead]:
    return service.list(db, project_id, task_status)


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskRead:
    return service.create(db, payload)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskRead:
    task = service.update(db, task_id, payload)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    if not service.delete(db, task_id):
        raise HTTPException(status_code=404, detail="Task not found")