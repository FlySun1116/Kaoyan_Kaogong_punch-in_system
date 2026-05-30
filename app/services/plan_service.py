from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Plan, Subject
from app.schemas.plan import PLAN_STATUSES, PLAN_TYPES, PlanCreate, PlanUpdate
from app.services.log_service import write_log
from app.utils.time_util import now_str, parse_date, today_str

CHILD_TYPE_MAP = {
    None: "total",
    "total": "month",
    "month": "week",
    "week": "day",
}


def get_plan_or_404(db: Session, plan_id: int, user_id: int) -> Plan:
    """查计划，验证归属"""
    plan: Plan | None = (
        db.query(Plan)
        .filter(Plan.id == plan_id, Plan.user_id == user_id)
        .first()
    )
    if plan is None:
        raise HTTPException(status_code=404, detail="计划不存在")
    return plan


def compute_status(
    plan: Plan,
    completion_rate: float | None = None,
) -> str:
    """纯计算：根据今日日期和完成率动态推计划状态"""
    today = parse_date(today_str())
    start = parse_date(plan.period_start)
    end_dt = parse_date(plan.period_end)

    if today < start:
        return "未开始"
    if today > end_dt:
        if completion_rate is not None and completion_rate >= 100:
            return "已完成"
        return "已过期"
    # 进行中
    if completion_rate is not None and completion_rate >= 100:
        return "已完成"
    return "进行中"


def _validate_plan_data(
    db: Session,
    user_id: int,
    plan_type: str,
    parent_id: int | None,
    period_start: str,
    period_end: str,
    subject_id: int | None,
) -> Plan | None:
    if plan_type not in PLAN_TYPES:
        raise HTTPException(status_code=400, detail="无效的计划类型")

    if parse_date(period_start) > parse_date(period_end):
        raise HTTPException(status_code=400, detail="开始日期不能晚于结束日期")

    if plan_type == "day" and period_start != period_end:
        raise HTTPException(status_code=400, detail="日计划的开始和结束日期必须相同")

    parent: Plan | None = None
    if parent_id is None:
        if plan_type != "total":
            raise HTTPException(status_code=400, detail="顶级计划必须是 total 类型")
    else:
        parent = get_plan_or_404(db, parent_id, user_id)
        expected_child = CHILD_TYPE_MAP.get(parent.plan_type)
        if expected_child != plan_type:
            raise HTTPException(
                status_code=400,
                detail=f"父计划类型为 {parent.plan_type}，子计划应为 {expected_child}",
            )
        if parse_date(period_start) < parse_date(parent.period_start):
            raise HTTPException(status_code=400, detail="子计划开始日期不能早于父计划")
        if parse_date(period_end) > parse_date(parent.period_end):
            raise HTTPException(status_code=400, detail="子计划结束日期不能晚于父计划")

    if subject_id is not None:
        subject = (
            db.query(Subject)
            .filter(Subject.id == subject_id, Subject.user_id == user_id)
            .first()
        )
        if subject is None:
            raise HTTPException(status_code=400, detail="关联科目不存在")

    return parent


def list_plans(
    db: Session,
    user_id: int,
    plan_type: str | None = None,
    parent_id: int | None = None,
) -> list[Plan]:
    query = db.query(Plan).filter(Plan.user_id == user_id)
    if plan_type:
        query = query.filter(Plan.plan_type == plan_type)
    if parent_id is not None:
        query = query.filter(Plan.parent_id == parent_id)
    plans: list[Plan] = query.order_by(Plan.sort_order, Plan.id).all()
    return plans


def create_plan(db: Session, user_id: int, data: PlanCreate) -> Plan:
    if data.status not in PLAN_STATUSES:
        raise HTTPException(status_code=400, detail="无效的计划状态")

    _validate_plan_data(
        db,
        user_id,
        data.plan_type,
        data.parent_id,
        data.period_start,
        data.period_end,
        data.subject_id,
    )

    now = now_str()
    plan = Plan(
        user_id=user_id,
        parent_id=data.parent_id,
        plan_type=data.plan_type,
        title=data.title,
        subject_id=data.subject_id,
        target_minutes=data.target_minutes,
        content=data.content,
        period_start=data.period_start,
        period_end=data.period_end,
        status=data.status,
        sort_order=data.sort_order,
        created_at=now,
        updated_at=now,
    )
    db.add(plan)
    db.flush()
    write_log(
        db, "create", "plan", plan.id,
        {"title": plan.title, "plan_type": plan.plan_type},
        actor_id=user_id,
    )
    db.commit()
    db.refresh(plan)
    return plan


def update_plan(db: Session, plan_id: int, user_id: int, data: PlanUpdate) -> Plan:
    plan = get_plan_or_404(db, plan_id, user_id)
    before = {
        "title": plan.title,
        "status": plan.status,
        "target_minutes": plan.target_minutes,
    }

    period_start = data.period_start or plan.period_start
    period_end = data.period_end or plan.period_end
    subject_id = plan.subject_id if data.subject_id is None else data.subject_id

    _validate_plan_data(
        db, user_id, plan.plan_type, plan.parent_id,
        period_start, period_end, subject_id,
    )

    if data.title is not None:
        plan.title = data.title
    if data.subject_id is not None:
        plan.subject_id = data.subject_id
    if data.target_minutes is not None:
        plan.target_minutes = data.target_minutes
    if data.content is not None:
        plan.content = data.content
    if data.period_start is not None:
        plan.period_start = data.period_start
    if data.period_end is not None:
        plan.period_end = data.period_end
    if data.status is not None:
        if data.status not in PLAN_STATUSES:
            raise HTTPException(status_code=400, detail="无效的计划状态")
        plan.status = data.status
    if data.sort_order is not None:
        plan.sort_order = data.sort_order

    plan.updated_at = now_str()
    write_log(
        db, "update", "plan", plan.id,
        {"before": before, "after": {"title": plan.title}},
        actor_id=user_id,
    )
    db.commit()
    db.refresh(plan)
    return plan


def delete_plan(db: Session, plan_id: int, user_id: int) -> None:
    plan = get_plan_or_404(db, plan_id, user_id)
    title = plan.title
    db.delete(plan)
    write_log(
        db, "delete", "plan", plan_id,
        {"title": title}, actor_id=user_id,
    )
    db.commit()


def get_plan_tree(db: Session, user_id: int, root_id: int | None = None) -> list[dict]:
    all_plans: list[Plan] = (
        db.query(Plan)
        .filter(Plan.user_id == user_id)
        .order_by(Plan.sort_order, Plan.id)
        .all()
    )
    children_map: dict[int | None, list[Plan]] = {}
    for plan in all_plans:
        children_map.setdefault(plan.parent_id, []).append(plan)

    if root_id is not None:
        roots = [get_plan_or_404(db, root_id, user_id)]
    else:
        # 顶级计划：parent_id 为 None
        roots = children_map.get(None, [])

    def build_node(plan: Plan) -> dict:
        # 动态计算状态
        dynamic_status = compute_status(plan)
        return {
            "id": plan.id,
            "parent_id": plan.parent_id,
            "plan_type": plan.plan_type,
            "title": plan.title,
            "subject_id": plan.subject_id,
            "target_minutes": plan.target_minutes,
            "content": plan.content,
            "period_start": plan.period_start,
            "period_end": plan.period_end,
            "status": dynamic_status,
            "sort_order": plan.sort_order,
            "created_at": plan.created_at,
            "updated_at": plan.updated_at,
            "children": [build_node(child) for child in children_map.get(plan.id, [])],
        }

    return [build_node(root) for root in roots]
