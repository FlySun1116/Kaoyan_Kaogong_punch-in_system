"""认证服务：注册、登录、用户查询"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import User
from app.security import hash_password, verify_password
from app.services.log_service import write_log
from app.services.subject_service import sync_templates_for_user
from app.utils.time_util import now_str


def get_user_by_id(db: Session, uid: int) -> User | None:
    return db.query(User).filter(User.id == uid).first()


def register(
    db: Session,
    username: str,
    password: str,
    exam_type: str = "考研",
    target_exam_date: str | None = None,
) -> User:
    """注册新用户，自动同步科目模板"""
    # 用户名查重
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    if exam_type not in ("考研", "考公"):
        raise HTTPException(status_code=400, detail="考试类型无效")

    user = User(
        username=username,
        password_hash=hash_password(password),
        role="user",
        exam_type=exam_type,
        target_exam_date=target_exam_date,
        created_at=now_str(),
    )
    db.add(user)
    db.flush()  # 获取 user.id

    # 同步科目模板
    sync_templates_for_user(db, user.id, exam_type)

    # 写日志（操作人 = 新用户自己）
    write_log(db, "register", "user", user.id, {"username": username}, actor_id=user.id)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, username: str, password: str) -> User:
    """校验用户名密码，返回用户；失败抛异常"""
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if user.is_active == 0:
        raise HTTPException(status_code=403, detail="账号已被禁用，请联系管理员")

    return user
