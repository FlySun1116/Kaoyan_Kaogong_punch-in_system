import json
import shutil
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import BACKUP_DIR, DATABASE_URL, EXPORT_DIR
from app.models import Backup, Plan, PunchRecord, Subject, SystemSetting, OperationLog
from app.services.log_service import write_log
from app.utils.time_util import now_str


def _db_path() -> Path:
    return Path(DATABASE_URL.replace("sqlite:///", ""))


def export_data(db: Session, user_id: int | None = None) -> dict:
    """导出数据（仅当前用户数据，管理员可导出全部）"""
    subject_query = db.query(Subject)
    plan_query = db.query(Plan)
    punch_query = db.query(PunchRecord)
    if user_id is not None:
        subject_query = subject_query.filter(Subject.user_id == user_id)
        plan_query = plan_query.filter(Plan.user_id == user_id)
        punch_query = punch_query.filter(PunchRecord.user_id == user_id)

    payload = {
        "exported_at": now_str(),
        "subjects": [row.__dict__ for row in subject_query.all()],
        "plans": [row.__dict__ for row in plan_query.all()],
        "punch_records": [row.__dict__ for row in punch_query.all()],
        "system_settings": [row.__dict__ for row in db.query(SystemSetting).all()],
        "operation_logs": [row.__dict__ for row in db.query(OperationLog).all()],
    }
    for key in payload:
        if isinstance(payload[key], list):
            for item in payload[key]:
                item.pop("_sa_instance_state", None)

    filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    file_path = EXPORT_DIR / filename
    file_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    write_log(
        db, "export", "backup", None,
        {"filename": filename, "type": "json"},
        actor_id=user_id,
    )
    db.commit()
    return {"filename": filename, "file_path": str(file_path), "file_size": file_path.stat().st_size}


def create_backup(db: Session, backup_type: str = "manual", actor_id: int | None = None) -> dict:
    src = _db_path()
    if not src.exists():
        raise HTTPException(status_code=404, detail="数据库文件不存在")

    filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    dest = BACKUP_DIR / filename
    shutil.copy2(src, dest)

    backup = Backup(
        filename=filename,
        file_path=str(dest),
        file_size=str(dest.stat().st_size),
        backup_type=backup_type,
        created_at=now_str(),
    )
    db.add(backup)
    write_log(
        db, "export", "backup", None,
        {"filename": filename, "type": "db"},
        actor_id=actor_id,
    )
    db.commit()
    db.refresh(backup)
    return {
        "id": backup.id,
        "filename": backup.filename,
        "file_path": backup.file_path,
        "file_size": backup.file_size,
        "backup_type": backup.backup_type,
        "created_at": backup.created_at,
    }


def list_backups(db: Session) -> list[Backup]:
    backups: list[Backup] = (
        db.query(Backup).order_by(Backup.created_at.desc()).all()
    )
    return backups


def list_exports() -> list[dict]:
    files = sorted(EXPORT_DIR.glob("export_*.json"), reverse=True)
    return [
        {"filename": f.name, "file_path": str(f), "file_size": f.stat().st_size}
        for f in files
    ]


def restore_backup(db: Session, backup_id: int, actor_id: int | None = None) -> dict:
    backup = db.query(Backup).filter(Backup.id == backup_id).first()
    if backup is None:
        raise HTTPException(status_code=404, detail="备份记录不存在")

    src = Path(backup.file_path)
    if not src.exists():
        raise HTTPException(status_code=404, detail="备份文件不存在")

    # 安全性：恢复前先自动备份当前库
    create_backup(db, backup_type="auto", actor_id=actor_id)

    # 释放数据库连接，然后覆盖
    from app.database import engine
    engine.dispose()

    dest = _db_path()
    shutil.copy2(src, dest)

    write_log(
        db, "restore", "backup", backup_id,
        {"filename": backup.filename}, actor_id=actor_id,
    )
    db.commit()
    return {"message": "恢复成功", "restored_from": backup.filename}
