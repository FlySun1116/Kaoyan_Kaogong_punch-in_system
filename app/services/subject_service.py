from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Subject, Plan, PunchRecord, SubjectTemplate
from app.schemas.subject import SubjectCreate, SubjectUpdate
from app.services.log_service import write_log
from app.utils.time_util import now_str


def sync_templates_for_user(db: Session, user_id: int, exam_type: str) -> None:
    """把该考试类型的科目模板同步为该用户的科目（已存在同名则跳过）"""
    templates = (
        db.query(SubjectTemplate)
        .filter(SubjectTemplate.exam_type == exam_type, SubjectTemplate.is_active == 1)
        .order_by(SubjectTemplate.sort_order)
        .all()
    )
    now = now_str()
    for tpl in templates:
        exists = (
            db.query(Subject)
            .filter(Subject.user_id == user_id, Subject.name == tpl.name)
            .first()
        )
        if exists:
            continue
        subject = Subject(
            user_id=user_id,
            name=tpl.name,
            weight=tpl.default_weight,
            sort_order=tpl.sort_order,
            is_activate=1,
            created_at=now,
            updated_at=now,
        )
        db.add(subject)
    if templates:
        db.flush()  # 不 commit，由调用方统一 commit


def get_subject_or_404(db: Session, subject_id: int, user_id: int) -> Subject:
    """查科目，验证归属；不存在或不属于该用户 → 404"""
    subject: Subject | None = (
        db.query(Subject)
        .filter(Subject.id == subject_id, Subject.user_id == user_id)
        .first()
    )
    if subject is None:
        raise HTTPException(status_code=404, detail="科目不存在")
    return subject


def list_subjects(
    db: Session,
    user_id: int,
    include_inactive: bool = False,
) -> list[Subject]:
    query = db.query(Subject).filter(Subject.user_id == user_id)
    if not include_inactive:
        query = query.filter(Subject.is_activate == 1)
    subjects: list[Subject] = query.order_by(Subject.sort_order, Subject.id).all()
    return subjects


def create_subject(db: Session, user_id: int, data: SubjectCreate) -> Subject:
    # 重名检查（同用户下）
    exists = (
        db.query(Subject)
        .filter(Subject.user_id == user_id, Subject.name == data.name)
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="科目名称已存在")

    now = now_str()
    subject = Subject(
        user_id=user_id,
        name=data.name,
        weight=data.weight,
        color=data.color,
        description=data.description,
        sort_order=data.sort_order,
        is_activate=1,
        created_at=now,
        updated_at=now,
    )
    db.add(subject)
    db.flush()  # 先拿到 id

    write_log(
        db, "create", "subject", subject.id,
        {"name": subject.name}, actor_id=user_id,
    )
    db.commit()
    db.refresh(subject)
    return subject


def update_subject(db: Session, subject_id: int, user_id: int, data: SubjectUpdate) -> Subject:
    subject = get_subject_or_404(db, subject_id, user_id)
    before = {
        "name": subject.name,
        "weight": subject.weight,
        "is_activate": subject.is_activate,
    }

    # 若改名称，检查重名（同用户下）
    if data.name and data.name != subject.name:
        exists = (
            db.query(Subject)
            .filter(Subject.user_id == user_id, Subject.name == data.name)
            .first()
        )
        if exists:
            raise HTTPException(status_code=400, detail="科目名称已存在")
        subject.name = data.name

    if data.weight is not None:
        subject.weight = data.weight
    if data.color is not None:
        subject.color = data.color
    if data.description is not None:
        subject.description = data.description
    if data.sort_order is not None:
        subject.sort_order = data.sort_order
    if data.is_activate is not None:
        subject.is_activate = data.is_activate

    subject.updated_at = now_str()

    write_log(
        db, "update", "subject", subject.id,
        {"before": before, "after": {"name": subject.name}},
        actor_id=user_id,
    )
    db.commit()
    db.refresh(subject)
    return subject


def delete_subject(db: Session, subject_id: int, user_id: int) -> None:
    """软删除：is_activate = 0"""
    subject = get_subject_or_404(db, subject_id, user_id)

    if subject.is_activate == 0:
        raise HTTPException(status_code=400, detail="科目已停用")

    subject.is_activate = 0
    subject.updated_at = now_str()

    write_log(
        db, "delete", "subject", subject.id,
        {"name": subject.name, "soft_delete": True},
        actor_id=user_id,
    )
    db.commit()


def hard_delete_subject(db: Session, subject_id: int, user_id: int) -> None:
    """物理删除（可选接口，慎用）若被计划或打卡引用，禁止删除"""
    subject = get_subject_or_404(db, subject_id, user_id)

    has_plan = db.query(Plan).filter(Plan.subject_id == subject_id).first()
    has_punch = db.query(PunchRecord).filter(PunchRecord.subject_id == subject_id).first()
    if has_plan or has_punch:
        raise HTTPException(
            status_code=400,
            detail="该科目已被计划或打卡引用，无法物理删除，请使用停用",
        )

    name = subject.name
    db.delete(subject)
    write_log(
        db, "delete", "subject", subject_id,
        {"name": name, "hard_delete": True},
        actor_id=user_id,
    )
    db.commit()
