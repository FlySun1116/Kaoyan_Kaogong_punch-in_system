"""管理员后台路由（全部需要 admin 权限）"""
from pathlib import Path

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models import User
from app.services import admin_service
from starlette.templating import Jinja2Templates

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter(prefix="/admin", tags=["管理后台"])


class UpdateSettingsRequest(BaseModel):
    updates: dict[str, str]


@router.get("")
def admin_page(
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """管理后台首页"""
    return templates.TemplateResponse(
        request,
        "admin.html",
        {
            "current_user": admin,
            "users": admin_service.list_users(db),
        },
    )


@router.get("/api/users")
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return admin_service.list_users(db)


@router.get("/api/users/{user_id}")
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    detail = admin_service.get_user_detail(db, user_id)
    # 清理 _sa_instance_state
    for key in ("subjects", "plans", "punch_records"):
        for item in detail.get(key, []):
            item.pop("_sa_instance_state", None)
    return detail


@router.post("/api/users/{user_id}/toggle-active")
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return admin_service.toggle_user_active(db, user_id, admin.id)


@router.get("/api/settings")
def get_settings(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return admin_service.admin_get_settings(db)


@router.put("/api/settings")
def update_settings(
    data: UpdateSettingsRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return admin_service.admin_update_settings(db, data.updates, admin.id)


@router.get("/api/logs")
def get_logs(
    user_id: int | None = Query(None),
    action: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return admin_service.get_logs(db, user_id, action, limit)
