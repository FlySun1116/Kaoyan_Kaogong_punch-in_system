from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.punch import PunchBatchCreate, PunchCreate, PunchResponse, PunchUpdate
from app.services import punch_service

router = APIRouter(prefix="/api/punches", tags=["每日打卡"])


@router.get("", response_model=list[PunchResponse])
def list_punches(
    punch_date: str | None = Query(None),
    subject_id: int | None = Query(None),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return punch_service.list_punches(
        db, user.id, punch_date, subject_id, start_date, end_date
    )


@router.get("/{punch_id}", response_model=PunchResponse)
def get_punch(
    punch_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return punch_service.get_punch_or_404(db, punch_id, user.id)


@router.post("", response_model=PunchResponse, status_code=201)
def create_punch(
    data: PunchCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return punch_service.create_or_update_punch(db, user.id, data)


@router.post("/batch", response_model=list[PunchResponse])
def batch_create_punches(
    data: PunchBatchCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return punch_service.batch_create_punches(db, user.id, data.records)


@router.put("/{punch_id}", response_model=PunchResponse)
def update_punch(
    punch_id: int,
    data: PunchUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return punch_service.update_punch(db, punch_id, user.id, data)


@router.delete("/{punch_id}", status_code=204)
def delete_punch(
    punch_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    punch_service.delete_punch(db, punch_id, user.id)
