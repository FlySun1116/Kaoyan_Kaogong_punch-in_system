#操作日志工具

import json

from sqlalchemy.orm import Session

from app.models import OperationLog
from app.utils.time_util import now_str


def write_log(
        db: Session,
        action: str,
        entity_type: str,
        entity_id: int | None = None,
        detail: dict | None = None,
        actor_id: int | None = None,
        target_user_id: int | None = None,
) -> None:
    """写入操作日志"""
    log = OperationLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        detail=json.dumps(detail, ensure_ascii=False) if detail else None,
        actor_id=actor_id,
        target_user_id=target_user_id,
        created_at=now_str(),
    )
    db.add(log)
