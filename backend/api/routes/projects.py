from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from backend.services.project import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])
service = ProjectService()


@router.get("", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)) -> list[ProjectRead]:
    return service.list(db)


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate, db: Session = Depends(get_db)
) -> ProjectRead:
    return service.create(db, payload)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)) -> ProjectRead:
    project = service.get(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)
) -> ProjectRead:
    project = service.update(db, project_id, payload)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project