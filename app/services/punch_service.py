from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import MakeupUsage, PunchRecord
from app.schemas.punch import PunchCreate, PunchUpdate
from app.services.log_service import write_log
from app.services.settings_service import get_setting_int
from app.services.subject_service import get_subject_or_404
from app.utils.time_util import now_str, parse_date


def _validate_punch_date(db: Session, punch_date: str) -> int:
    try:
        target = parse_date(punch_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="日期格式应为 YYYY-MM-DD") from exc

    today = date.today()
    if target > today:
        raise HTTPException(status_code=400, detail="不能为未来日期打卡")

    makeup_limit = get_setting_int(db, "makeup_limit", 7)
    if (today - target).days > makeup_limit:
        raise HTTPException(status_code=400, detail=f"仅支持近 {makeup_limit} 天内补卡")

    return 1 if target < today else 0


def get_punch_or_404(db: Session, punch_id: int, user_id: int) -> PunchRecord:
    record: PunchRecord | None = (
        db.query(PunchRecord)
        .filter(PunchRecord.id == punch_id, PunchRecord.user_id == user_id)
        .first()
    )
    if record is None:
        raise HTTPException(status_code=404, detail="打卡记录不存在")
    return record


def list_punches(
    db: Session,
    user_id: int,
    punch_date: str | None = None,
    subject_id: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[PunchRecord]:
    query = db.query(PunchRecord).filter(PunchRecord.user_id == user_id)
    if punch_date:
        query = query.filter(PunchRecord.punch_date == punch_date)
    if subject_id:
        query = query.filter(PunchRecord.subject_id == subject_id)
    if start_date:
        query = query.filter(PunchRecord.punch_date >= start_date)
    if end_date:
        query = query.filter(PunchRecord.punch_date <= end_date)
    records: list[PunchRecord] = query.order_by(
        PunchRecord.punch_date.desc(), PunchRecord.id.desc()
    ).all()
    return records


def _check_and_count_makeup(db: Session, user_id: int, punch_date: str) -> None:
    """
    检查并扣减每月补卡额度。
    仅对 is_makeup=1 的新记录计数；更新已有记录不重复计数。
    调用前确保已判定 is_makeup=1。
    """
    year_month = punch_date[:7]  # 截取 YYYY-MM
    monthly_limit = get_setting_int(db, "makeup_monthly_limit", 5)

    usage = (
        db.query(MakeupUsage)
        .filter(MakeupUsage.user_id == user_id, MakeupUsage.year_month == year_month)
        .first()
    )
    if usage is None:
        usage = MakeupUsage(
            user_id=user_id,
            year_month=year_month,
            used_count=0,
            updated_at=now_str(),
        )
        db.add(usage)
        db.flush()

    if usage.used_count >= monthly_limit:
        raise HTTPException(
            status_code=400,
            detail=f"当月补卡次数已达上限（{monthly_limit} 次）",
        )

    usage.used_count += 1
    usage.updated_at = now_str()


def create_or_update_punch(db: Session, user_id: int, data: PunchCreate) -> PunchRecord:
    get_subject_or_404(db, data.subject_id, user_id)
    is_makeup = _validate_punch_date(db, data.punch_date)
    now = now_str()

    existing: PunchRecord | None = (
        db.query(PunchRecord)
        .filter(
            PunchRecord.user_id == user_id,
            PunchRecord.punch_date == data.punch_date,
            PunchRecord.subject_id == data.subject_id,
        )
        .first()
    )

    if existing:
        # 更新已有记录 — 不重复计补卡次数
        existing.actual_minutes = data.actual_minutes
        existing.content = data.content
        existing.is_makeup = is_makeup
        existing.updated_at = now
        write_log(
            db, "update", "punch", existing.id,
            {"punch_date": data.punch_date}, actor_id=user_id,
        )
        db.commit()
        db.refresh(existing)
        return existing

    # 新记录：若为补卡，检查/扣减月度额度
    if is_makeup:
        _check_and_count_makeup(db, user_id, data.punch_date)

    record = PunchRecord(
        user_id=user_id,
        punch_date=data.punch_date,
        subject_id=data.subject_id,
        actual_minutes=data.actual_minutes,
        content=data.content,
        is_makeup=is_makeup,
        created_at=now,
        updated_at=now,
    )
    db.add(record)
    db.flush()
    write_log(
        db, "create", "punch", record.id,
        {"punch_date": data.punch_date}, actor_id=user_id,
    )
    db.commit()
    db.refresh(record)
    return record


def batch_create_punches(db: Session, user_id: int, records: list[PunchCreate]) -> list[PunchRecord]:
    """
    批量打卡 — 整批共用一次 commit，中途异常则 rollback 全部回滚。
    """
    results: list[PunchRecord] = []
    try:
        for item in records:
            # 使用内部逻辑而非 create_or_update_punch（避免中间 commit）
            get_subject_or_404(db, item.subject_id, user_id)
            is_makeup = _validate_punch_date(db, item.punch_date)
            now = now_str()

            existing: PunchRecord | None = (
                db.query(PunchRecord)
                .filter(
                    PunchRecord.user_id == user_id,
                    PunchRecord.punch_date == item.punch_date,
                    PunchRecord.subject_id == item.subject_id,
                )
                .first()
            )

            if existing:
                existing.actual_minutes = item.actual_minutes
                existing.content = item.content
                existing.is_makeup = is_makeup
                existing.updated_at = now
                results.append(existing)
                continue

            if is_makeup:
                _check_and_count_makeup(db, user_id, item.punch_date)

            record = PunchRecord(
                user_id=user_id,
                punch_date=item.punch_date,
                subject_id=item.subject_id,
                actual_minutes=item.actual_minutes,
                content=item.content,
                is_makeup=is_makeup,
                created_at=now,
                updated_at=now,
            )
            db.add(record)
            db.flush()
            write_log(
                db, "create", "punch", record.id,
                {"punch_date": item.punch_date}, actor_id=user_id,
            )
            results.append(record)

        db.commit()
        for r in results:
            db.refresh(r)
        return results
    except Exception:
        db.rollback()
        raise


def update_punch(db: Session, punch_id: int, user_id: int, data: PunchUpdate) -> PunchRecord:
    record = get_punch_or_404(db, punch_id, user_id)
    before = {"actual_minutes": record.actual_minutes, "content": record.content}

    if data.actual_minutes is not None:
        record.actual_minutes = data.actual_minutes
    if data.content is not None:
        record.content = data.content
    record.updated_at = now_str()

    write_log(
        db, "update", "punch", record.id,
        {"before": before}, actor_id=user_id,
    )
    db.commit()
    db.refresh(record)
    return record


def delete_punch(db: Session, punch_id: int, user_id: int) -> None:
    record = get_punch_or_404(db, punch_id, user_id)
    detail = {"punch_date": record.punch_date, "subject_id": record.subject_id}
    db.delete(record)
    write_log(
        db, "delete", "punch", punch_id, detail,
        actor_id=user_id,
    )
    db.commit()
