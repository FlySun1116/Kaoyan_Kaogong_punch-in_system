from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Plan, PunchRecord, Subject
from app.services.settings_service import get_setting_int
from app.utils.time_util import days_between, parse_date, today_str


def _sum_punch_minutes(
    db: Session,
    user_id: int,
    start_date: str,
    end_date: str,
    subject_id: int | None = None,
) -> int:
    query = (
        db.query(func.coalesce(func.sum(PunchRecord.actual_minutes), 0))
        .filter(
            PunchRecord.user_id == user_id,
            PunchRecord.punch_date >= start_date,
            PunchRecord.punch_date <= end_date,
        )
    )
    if subject_id:
        query = query.filter(PunchRecord.subject_id == subject_id)
    return int(query.scalar() or 0)


def _sum_day_plan_targets(
    db: Session,
    user_id: int,
    start_date: str,
    end_date: str,
    subject_id: int | None = None,
) -> int:
    query = (
        db.query(func.coalesce(func.sum(Plan.target_minutes), 0))
        .filter(
            Plan.user_id == user_id,
            Plan.plan_type == "day",
            Plan.period_start >= start_date,
            Plan.period_end <= end_date,
        )
    )
    if subject_id:
        query = query.filter(Plan.subject_id == subject_id)
    return int(query.scalar() or 0)


def completion_rate(actual: int, target: int) -> float | None:
    """
    完成率。
    当 target <= 0 时返回 None（表示「未设目标」），不要返回 100。
    """
    if target <= 0:
        return None
    return round(min(actual / target * 100, 100.0), 2)


def get_progress_overview(db: Session, user_id: int) -> dict:
    today = today_str()
    week_start = (date.today() - timedelta(days=date.today().weekday())).strftime("%Y-%m-%d")

    day_target = _sum_day_plan_targets(db, user_id, today, today)
    day_actual = _sum_punch_minutes(db, user_id, today, today)

    week_target = _sum_day_plan_targets(db, user_id, week_start, today)
    week_actual = _sum_punch_minutes(db, user_id, week_start, today)

    total_target = int(
        db.query(func.coalesce(func.sum(Plan.target_minutes), 0))
        .filter(Plan.user_id == user_id, Plan.plan_type == "day")
        .scalar()
        or 0
    )
    total_actual = int(
        db.query(func.coalesce(func.sum(PunchRecord.actual_minutes), 0))
        .filter(PunchRecord.user_id == user_id)
        .scalar()
        or 0
    )

    warning_threshold = get_setting_int(db, "warning_threshold", 60)
    day_rate = completion_rate(day_actual, day_target)

    # None 不触发预警
    warning = (day_rate is not None and day_rate < warning_threshold)

    return {
        "today": {
            "target_minutes": day_target,
            "actual_minutes": day_actual,
            "completion_rate": day_rate,
        },
        "week": {
            "target_minutes": week_target,
            "actual_minutes": week_actual,
            "completion_rate": completion_rate(week_actual, week_target),
        },
        "total": {
            "target_minutes": total_target,
            "actual_minutes": total_actual,
            "completion_rate": completion_rate(total_actual, total_target),
        },
        "warning": warning,
        "warning_threshold": warning_threshold,
    }


def get_subject_stats(db: Session, user_id: int) -> list[dict]:
    subjects = (
        db.query(Subject)
        .filter(Subject.user_id == user_id, Subject.is_activate == 1)
        .all()
    )
    result: list[dict] = []
    for subject in subjects:
        total_minutes = int(
            db.query(func.coalesce(func.sum(PunchRecord.actual_minutes), 0))
            .filter(
                PunchRecord.user_id == user_id,
                PunchRecord.subject_id == subject.id,
            )
            .scalar()
            or 0
        )
        punch_days = (
            db.query(func.count(func.distinct(PunchRecord.punch_date)))
            .filter(
                PunchRecord.user_id == user_id,
                PunchRecord.subject_id == subject.id,
            )
            .scalar()
            or 0
        )
        avg_minutes = round(total_minutes / punch_days, 2) if punch_days else 0
        result.append(
            {
                "subject_id": subject.id,
                "subject_name": subject.name,
                "weight": subject.weight,
                "total_minutes": total_minutes,
                "punch_days": int(punch_days),
                "avg_minutes_per_day": avg_minutes,
            }
        )
    return result


def get_punch_rate(db: Session, user_id: int, start_date: str, end_date: str) -> dict:
    total_days = days_between(start_date, end_date)
    punched_days = (
        db.query(func.count(func.distinct(PunchRecord.punch_date)))
        .filter(
            PunchRecord.user_id == user_id,
            PunchRecord.punch_date >= start_date,
            PunchRecord.punch_date <= end_date,
        )
        .scalar()
        or 0
    )
    rate = round(punched_days / total_days * 100, 2) if total_days else 0
    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_days": total_days,
        "punched_days": int(punched_days),
        "punch_rate": rate,
    }


def get_study_trend(db: Session, user_id: int, start_date: str, end_date: str) -> list[dict]:
    rows = (
        db.query(
            PunchRecord.punch_date,
            func.sum(PunchRecord.actual_minutes).label("minutes"),
        )
        .filter(
            PunchRecord.user_id == user_id,
            PunchRecord.punch_date >= start_date,
            PunchRecord.punch_date <= end_date,
        )
        .group_by(PunchRecord.punch_date)
        .order_by(PunchRecord.punch_date)
        .all()
    )
    return [{"date": row.punch_date, "minutes": int(row.minutes)} for row in rows]


def get_plan_progress(db: Session, user_id: int, plan_id: int) -> dict:
    from app.services.plan_service import get_plan_or_404

    plan = get_plan_or_404(db, plan_id, user_id)
    actual = _sum_punch_minutes(
        db, user_id, plan.period_start, plan.period_end, plan.subject_id
    )
    if plan.plan_type == "day":
        target = plan.target_minutes
    else:
        target = _sum_day_plan_targets(
            db, user_id, plan.period_start, plan.period_end, plan.subject_id
        )
    return {
        "plan_id": plan.id,
        "title": plan.title,
        "plan_type": plan.plan_type,
        "period_start": plan.period_start,
        "period_end": plan.period_end,
        "target_minutes": target,
        "actual_minutes": actual,
        "completion_rate": completion_rate(actual, target),
    }


def ascii_line_chart(trend: list[dict], width: int = 40) -> str:
    if not trend:
        return "(暂无数据)"
    max_val = max(item["minutes"] for item in trend) or 1
    lines: list[str] = []
    for item in trend:
        bar_len = int(item["minutes"] / max_val * width)
        bar = "█" * bar_len
        lines.append(f"{item['date']} | {bar} {item['minutes']}min")
    return "\n".join(lines)
