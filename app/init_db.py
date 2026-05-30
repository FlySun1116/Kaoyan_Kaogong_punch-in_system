"""
数据库初始化与迁移
- 若旧库 subjects 表无 user_id 列 → 重命名备份旧库，新建空库
- 建所有表（Base.metadata.create_all）
- 种子数据（幂等）
"""
import shutil
from datetime import datetime
from pathlib import Path

from app.config import DATA_DIR, BACKUP_DIR
from app.database import Base, engine, SessionLocal
from app.models import (  # noqa: F401  — 确保所有模型注册到 Base
    Subject,
    Plan,
    PunchRecord,
    SystemSetting,
    OperationLog,
    Backup,
    User,
    SubjectTemplate,
    MakeupUsage,
)
from app.security import hash_password
from app.utils.time_util import now_str


DB_PATH = DATA_DIR / "Kykg_punch-in_system.db"


def _legacy_db_has_user_id() -> bool:
    """检测旧库 subjects 表是否已有 user_id 列"""
    import sqlite3
    if not DB_PATH.exists():
        return False  # 无旧库
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.execute("PRAGMA table_info(subjects)")
        cols = [row[1] for row in cursor.fetchall()]
        conn.close()
        return "user_id" in cols
    except Exception:
        return False


def _backup_legacy_db():
    """重命名备份旧库"""
    BACKUP_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"legacy_{ts}.db"
    shutil.move(str(DB_PATH), str(dest))
    print(f"[init_db] 旧库已备份至: {dest}")
    return dest


def _seed_admin():
    """创建管理员账号（管理员首次登录后应修改密码）"""
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == "admin").first()
        if existing:
            return
        user = User(
            username="admin",
            password_hash=hash_password("admin123"),
            role="admin",
            exam_type="考研",
            created_at=now_str(),
        )
        db.add(user)
        db.commit()
        print("[init_db] 管理员账号已创建: admin / admin123")
    finally:
        db.close()


def _seed_templates():
    """创建科目模板（幂等）"""
    db = SessionLocal()
    try:
        existing = db.query(SubjectTemplate).first()
        if existing:
            return

        templates = [
            # 考研
            ("考研", "政治", 1.0, 1),
            ("考研", "英语", 1.0, 2),
            ("考研", "数学", 1.0, 3),
            ("考研", "专业课", 1.0, 4),
            # 考公
            ("考公", "行测", 1.0, 1),
            ("考公", "申论", 1.0, 2),
            ("考公", "面试", 1.0, 3),
        ]
        now = now_str()
        for exam_type, name, weight, sort_order in templates:
            db.add(SubjectTemplate(
                exam_type=exam_type,
                name=name,
                default_weight=weight,
                sort_order=sort_order,
                created_at=now,
            ))
        db.commit()
        print(f"[init_db] 科目模板已创建: {len(templates)} 条")
    finally:
        db.close()


def _seed_settings():
    """创建全局配置默认值（幂等）"""
    db = SessionLocal()
    try:
        defaults = {
            "makeup_limit": "7",
            "makeup_monthly_limit": "5",
            "warning_threshold": "60",
            "daily_target_minutes": "480",
        }
        now = now_str()
        created = 0
        for key, value in defaults.items():
            existing = db.query(SystemSetting).filter(SystemSetting.key == key).first()
            if existing:
                continue
            db.add(SystemSetting(key=key, value=value, updated_at=now))
            created += 1
        if created:
            db.commit()
            print(f"[init_db] 全局配置已创建: {created} 项")
    finally:
        db.close()


def init():
    """
    应用启动时调用一次。
    1. 检查并迁移旧库
    2. 建表
    3. 种子
    """
    # 步骤 1：旧库检测与迁移
    if DB_PATH.exists() and not _legacy_db_has_user_id():
        print("[init_db] 检测到旧版数据库（无 user_id），开始迁移…")
        _backup_legacy_db()

    # 步骤 2：建表（使用 SQLAlchemy create_all）
    Base.metadata.create_all(bind=engine)
    print("[init_db] 数据库表已就绪")

    # 步骤 3：种子
    _seed_admin()
    _seed_templates()
    _seed_settings()
