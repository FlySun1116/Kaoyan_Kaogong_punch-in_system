from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.subject import SubjectCreate, SubjectResponse, SubjectUpdate
from app.services import subject_service

router = APIRouter(prefix="/api/subjects", tags=["科目管理"])


@router.get("", response_model=list[SubjectResponse])
def list_subjects(
    include_inactive: bool = Query(False, description="是否包含已停用科目"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return subject_service.list_subjects(db, user.id, include_inactive)


@router.get("/{subject_id}", response_model=SubjectResponse)
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return subject_service.get_subject_or_404(db, subject_id, user.id)


@router.post("", response_model=SubjectResponse, status_code=201)
def create_subject(
    data: SubjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return subject_service.create_subject(db, user.id, data)


@router.put("/{subject_id}", response_model=SubjectResponse)
def update_subject(
    subject_id: int,
    data: SubjectUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return subject_service.update_subject(db, subject_id, user.id, data)


@router.delete("/{subject_id}", status_code=204)
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """软删除（停用）"""
    subject_service.delete_subject(db, subject_id, user.id)


@router.delete("/{subject_id}/hard", status_code=204)
def hard_delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """物理删除（无引用时）"""
    subject_service.hard_delete_subject(db, subject_id, user.id)


@router.post("/sync-templates")
def sync_templates(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """从模板导入科目（幂等）"""
    subject_service.sync_templates_for_user(db, user.id, user.exam_type)
    return {"ok": True, "message": f"已同步 {user.exam_type} 科目模板"}
