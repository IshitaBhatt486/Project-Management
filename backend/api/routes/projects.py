from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.api.dependencies import get_current_user
from backend.db.models import User
from backend.db.session import get_db
from backend.schemas.project import ProjectCreate, ProjectList, ProjectRead, ProjectUpdate
from backend.services.project_access import require_project_role
from backend.services.project import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])
service = ProjectService()


@router.get("", response_model=ProjectList)
def list_projects(
    search: str | None = Query(default=None, max_length=120),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=50, alias="pageSize"),
    project_status: str | None = Query(default=None, alias="status"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectList:
    return service.list(db, user.id, search, project_status, page, page_size)


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectRead:
    return service.create(db, payload, user.id)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectRead:
    project = service.get(db, project_id, user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectRead:
    membership = require_project_role(db, project_id, user.id, {"owner", "admin"})
    if payload.status == "archived" and membership.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can archive a project",
        )
    project = service.update(db, project_id, user.id, payload)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/archive", response_model=ProjectRead)
def archive_project(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectRead:
    require_project_role(db, project_id, user.id, {"owner"})
    project = service.archive(db, project_id, user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    require_project_role(db, project_id, user.id, {"owner"})
    if not service.delete(db, project_id, user.id):
        raise HTTPException(status_code=404, detail="Project not found")