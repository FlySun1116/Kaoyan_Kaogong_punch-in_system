from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models import User
from app.services import data_service

router = APIRouter(prefix="/api/data", tags=["数据管理"])


@router.post("/export")
def export_data(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return data_service.export_data(db, user.id)


@router.post("/backup")
def create_backup(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return data_service.create_backup(db, backup_type="manual", actor_id=admin.id)


@router.get("/backups")
def list_backups(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return data_service.list_backups(db)


@router.get("/exports")
def list_exports(
    user: User = Depends(get_current_user),
):
    return data_service.list_exports()


@router.post("/restore/{backup_id}")
def restore_backup(
    backup_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return data_service.restore_backup(db, backup_id, actor_id=admin.id)
