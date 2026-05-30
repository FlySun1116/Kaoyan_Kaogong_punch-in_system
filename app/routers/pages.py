from datetime import date, timedelta
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from app.database import get_db
from app.dependencies import get_current_user, get_current_user_optional
from app.models import User
from app.services import plan_service, punch_service, settings_service, stats_service, subject_service
from app.services import data_service
from app.utils.time_util import today_str

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter(tags=["页面"])


def _require_login(request: Request, user: User | None):
    """未登录 → 重定向 /login"""
    if user is None:
        return RedirectResponse("/login", status_code=302)
    return None


@router.get("/")
def home(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    redirect = _require_login(request, user)
    if redirect:
        return redirect
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "current_user": user,
            "overview": stats_service.get_progress_overview(db, user.id),
            "settings": {
                "exam_type": user.exam_type,
                "exam_date": user.target_exam_date or "-",
                "daily_target_minutes": settings_service.get_setting(db, "daily_target_minutes", "480"),
            },
            "today": today_str(),
        },
    )


@router.get("/subjects")
def subjects_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    redirect = _require_login(request, user)
    if redirect:
        return redirect
    return templates.TemplateResponse(
        request,
        "subjects.html",
        {
            "current_user": user,
            "subjects": subject_service.list_subjects(db, user.id, include_inactive=True),
        },
    )


@router.get("/plans")
def plans_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    redirect = _require_login(request, user)
    if redirect:
        return redirect
    tree = plan_service.get_plan_tree(db, user.id)
    # 可作父级的计划（日计划是叶子，不能再有子计划）
    plan_parents = [
        p for p in plan_service.list_plans(db, user.id) if p.plan_type != "day"
    ]
    return templates.TemplateResponse(
        request,
        "plans.html",
        {
            "current_user": user,
            "plans_tree": tree,
            "plan_parents": plan_parents,
            "subjects": subject_service.list_subjects(db, user.id),
        },
    )


@router.get("/punch")
def punch_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    redirect = _require_login(request, user)
    if redirect:
        return redirect
    subjects = subject_service.list_subjects(db, user.id)
    subject_map = {s.id: s.name for s in subjects}
    return templates.TemplateResponse(
        request,
        "punch.html",
        {
            "current_user": user,
            "subjects": subjects,
            "subject_map": subject_map,
            "today": today_str(),
            "records": punch_service.list_punches(db, user.id, punch_date=today_str()),
            "makeup_limit": settings_service.get_setting_int(db, "makeup_limit", 7),
        },
    )


@router.get("/progress")
def progress_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    redirect = _require_login(request, user)
    if redirect:
        return redirect
    return templates.TemplateResponse(
        request,
        "progress.html",
        {
            "current_user": user,
            "overview": stats_service.get_progress_overview(db, user.id),
            "subject_stats": stats_service.get_subject_stats(db, user.id),
        },
    )


@router.get("/stats")
def stats_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    redirect = _require_login(request, user)
    if redirect:
        return redirect
    end_date = date.today().strftime("%Y-%m-%d")
    start_date = (date.today() - timedelta(days=13)).strftime("%Y-%m-%d")
    trend = stats_service.get_study_trend(db, user.id, start_date, end_date)
    return templates.TemplateResponse(
        request,
        "stats.html",
        {
            "current_user": user,
            "subject_stats": stats_service.get_subject_stats(db, user.id),
            "punch_rate": stats_service.get_punch_rate(
                db,
                user.id,
                (date.today() - timedelta(days=29)).strftime("%Y-%m-%d"),
                end_date,
            ),
            "trend": trend,
            "chart": stats_service.ascii_line_chart(trend),
        },
    )


@router.get("/data-manage")
def data_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    redirect = _require_login(request, user)
    if redirect:
        return redirect
    return templates.TemplateResponse(
        request,
        "data.html",
        {
            "current_user": user,
            "backups": data_service.list_backups(db),
            "exports": data_service.list_exports(),
        },
    )
