"""管理员服务：用户管理、日志查询"""
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import (
    OperationLog,
    Plan,
    PunchRecord,
    Subject,
    SystemSetting,
    User,
)
from app.services.log_service import write_log
from app.services.settings_service import update_settings_batch
from app.utils.time_util import now_str


def list_users(db: Session) -> list[dict]:
    """用户列表（含概况统计）"""
    users = db.query(User).order_by(User.id).all()
    result = []
    for u in users:
        subject_count = (
            db.query(func.count(Subject.id))
            .filter(Subject.user_id == u.id)
            .scalar()
            or 0
        )
        punch_count = (
            db.query(func.count(PunchRecord.id))
            .filter(PunchRecord.user_id == u.id)
            .scalar()
            or 0
        )
        plan_count = (
            db.query(func.count(Plan.id))
            .filter(Plan.user_id == u.id)
            .scalar()
            or 0
        )
        result.append({
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "exam_type": u.exam_type,
            "target_exam_date": u.target_exam_date,
            "is_active": u.is_active,
            "created_at": u.created_at,
            "subject_count": int(subject_count),
            "punch_count": int(punch_count),
            "plan_count": int(plan_count),
        })
    return result


def get_user_detail(db: Session, user_id: int) -> dict:
    """单用户详情"""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    subjects = db.query(Subject).filter(Subject.user_id == user_id).all()
    plans = db.query(Plan).filter(Plan.user_id == user_id).all()
    punches = db.query(PunchRecord).filter(PunchRecord.user_id == user_id).all()

    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "exam_type": user.exam_type,
        "target_exam_date": user.target_exam_date,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "subjects": [s.__dict__ for s in subjects],
        "plans": [p.__dict__ for p in plans],
        "punch_records": [r.__dict__ for r in punches],
    }


def toggle_user_active(db: Session, user_id: int, actor_id: int) -> dict:
    """启用/禁用用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user.role == "admin":
        raise HTTPException(status_code=400, detail="不能禁用管理员账号")

    user.is_active = 1 if user.is_active == 0 else 0
    new_state = "启用" if user.is_active else "禁用"

    write_log(
        db,
        "toggle_active",
        "user",
        user.id,
        {"action": new_state, "username": user.username},
        actor_id=actor_id,
        target_user_id=user.id,
    )
    db.commit()
    return {"user_id": user.id, "username": user.username, "is_active": user.is_active}


def admin_get_settings(db: Session) -> dict[str, str]:
    """管理员查看全局配置"""
    rows = db.query(SystemSetting).all()
    return {row.key: row.value for row in rows}


def admin_update_settings(
    db: Session,
    updates: dict[str, str],
    actor_id: int,
) -> dict[str, str]:
    """管理员修改全局配置"""
    update_settings_batch(db, updates, updated_by=actor_id)
    write_log(
        db,
        "update_settings",
        "system",
        None,
        {"updates": updates},
        actor_id=actor_id,
    )
    return admin_get_settings(db)


def get_logs(
    db: Session,
    user_id: int | None = None,
    action: str | None = None,
    limit: int = 100,
) -> list[dict]:
    """查询操作日志"""
    query = db.query(OperationLog)
    if user_id:
        query = query.filter(
            (OperationLog.actor_id == user_id)
            | (OperationLog.target_user_id == user_id)
        )
    if action:
        query = query.filter(OperationLog.action == action)
    logs = query.order_by(OperationLog.id.desc()).limit(limit).all()
    result = []
    for log in logs:
        result.append({
            "id": log.id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "detail": log.detail,
            "actor_id": log.actor_id,
            "target_user_id": log.target_user_id,
            "created_at": log.created_at,
        })
    return result
