from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.plan import PlanCreate, PlanResponse, PlanUpdate
from app.services import plan_service

router = APIRouter(prefix="/api/plans", tags=["计划管理"])


@router.get("", response_model=list[PlanResponse])
def list_plans(
    plan_type: str | None = Query(None, description="按类型筛选"),
    parent_id: int | None = Query(None, description="按父计划筛选"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return plan_service.list_plans(db, user.id, plan_type, parent_id)


@router.get("/tree")
def get_plan_tree(
    root_id: int | None = Query(None, description="指定根计划 ID"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return plan_service.get_plan_tree(db, user.id, root_id)


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return plan_service.get_plan_or_404(db, plan_id, user.id)


@router.post("", response_model=PlanResponse, status_code=201)
def create_plan(
    data: PlanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return plan_service.create_plan(db, user.id, data)


@router.put("/{plan_id}", response_model=PlanResponse)
def update_plan(
    plan_id: int,
    data: PlanUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return plan_service.update_plan(db, plan_id, user.id, data)


@router.delete("/{plan_id}", status_code=204)
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    plan_service.delete_plan(db, plan_id, user.id)
