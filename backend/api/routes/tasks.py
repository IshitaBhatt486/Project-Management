from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.api.dependencies import get_current_user
from backend.db.models import User
from backend.db.session import get_db
from backend.schemas.task import TaskCreate, TaskRead, TaskStatus, TaskUpdate
from backend.services.task import TaskService
from backend.services.project_access import require_project_role

router = APIRouter(prefix="/tasks", tags=["tasks"])
service = TaskService()


@router.get("", response_model=list[TaskRead])
def list_tasks(
    project_id: int | None = Query(default=None, alias="projectId"),
    task_status: TaskStatus | None = Query(default=None, alias="status"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TaskRead]:
    return service.list(db, user.id, project_id, task_status)


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskRead:
    require_project_role(db, payload.project_id, user.id, {"owner", "admin"})
    task = service.create(db, payload, user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Project not found")
    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskRead:
    project_id = service.project_id_for_task(db, task_id, user.id)
    if project_id is None:
        raise HTTPException(status_code=404, detail="Task not found")
    require_project_role(db, project_id, user.id, {"owner", "admin"})
    task = service.update(db, task_id, user.id, payload)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    project_id = service.project_id_for_task(db, task_id, user.id)
    if project_id is None:
        raise HTTPException(status_code=404, detail="Task not found")
    require_project_role(db, project_id, user.id, {"owner", "admin"})
    if not service.delete(db, task_id, user.id):
        raise HTTPException(status_code=404, detail="Task not found")
