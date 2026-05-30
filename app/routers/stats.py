from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.services import stats_service

router = APIRouter(prefix="/api/stats", tags=["统计分析"])


@router.get("/overview")
def progress_overview(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return stats_service.get_progress_overview(db, user.id)


@router.get("/subjects")
def subject_stats(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return stats_service.get_subject_stats(db, user.id)


@router.get("/punch-rate")
def punch_rate(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not end_date:
        end_date = date.today().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (date.today() - timedelta(days=29)).strftime("%Y-%m-%d")
    return stats_service.get_punch_rate(db, user.id, start_date, end_date)


@router.get("/trend")
def study_trend(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not end_date:
        end_date = date.today().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (date.today() - timedelta(days=13)).strftime("%Y-%m-%d")
    trend = stats_service.get_study_trend(db, user.id, start_date, end_date)
    return {
        "start_date": start_date,
        "end_date": end_date,
        "data": trend,
        "chart": stats_service.ascii_line_chart(trend),
    }


@router.get("/plans/{plan_id}")
def plan_progress(
    plan_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return stats_service.get_plan_progress(db, user.id, plan_id)
