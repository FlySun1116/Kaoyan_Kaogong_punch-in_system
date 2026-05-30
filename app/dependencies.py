"""鉴权依赖（FastAPI Depends）"""
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """从 session 取当前登录用户；未登录/被禁用 → 401"""
    uid = request.session.get("user_id")
    if uid is None:
        raise HTTPException(status_code=401, detail="请先登录")

    user: User | None = db.query(User).filter(User.id == uid).first()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")

    if user.is_active == 0:
        raise HTTPException(status_code=403, detail="账号已被禁用")

    return user


def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
) -> User | None:
    """页面用：未登录返回 None，不抛异常"""
    uid = request.session.get("user_id")
    if uid is None:
        return None
    user: User | None = db.query(User).filter(User.id == uid).first()
    if user is None or user.is_active == 0:
        return None
    return user


def require_admin(
    user: User = Depends(get_current_user),
) -> User:
    """需要管理员角色，否则 403"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user
