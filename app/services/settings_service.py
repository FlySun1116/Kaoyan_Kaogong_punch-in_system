from sqlalchemy.orm import Session

from app.models import SystemSetting
from app.utils.time_util import now_str


def get_setting(db: Session, key: str, default: str = "") -> str:
    row = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    return row.value if row else default


def get_setting_int(db: Session, key: str, default: int = 0) -> int:
    value = get_setting(db, key, str(default))
    try:
        return int(value)
    except ValueError:
        return default


def get_all_settings(db: Session) -> dict[str, str]:
    rows = db.query(SystemSetting).all()
    return {row.key: row.value for row in rows}


def set_setting(
    db: Session,
    key: str,
    value: str,
    updated_by: int | None = None,
) -> None:
    """写入/更新单个配置"""
    row = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if row:
        row.value = value
        row.updated_by = updated_by
        row.updated_at = now_str()
    else:
        row = SystemSetting(
            key=key,
            value=value,
            updated_by=updated_by,
            updated_at=now_str(),
        )
        db.add(row)
    db.commit()


def update_settings_batch(
    db: Session,
    updates: dict[str, str],
    updated_by: int | None = None,
) -> None:
    """批量更新配置"""
    now = now_str()
    for key, value in updates.items():
        row = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if row:
            row.value = value
            row.updated_by = updated_by
            row.updated_at = now
        else:
            db.add(SystemSetting(
                key=key,
                value=value,
                updated_by=updated_by,
                updated_at=now,
            ))
    db.commit()
