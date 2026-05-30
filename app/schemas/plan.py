from pydantic import BaseModel, Field


PLAN_TYPES = ("total", "month", "week", "day")
PLAN_STATUSES = ("未开始", "进行中", "已完成", "已过期")


class PlanBase(BaseModel):
    plan_type: str = Field(..., description="total/month/week/day")
    title: str = Field(..., min_length=1, max_length=100)
    subject_id: int | None = None
    target_minutes: int = Field(default=0, ge=0)
    content: str | None = None
    period_start: str = Field(..., description="YYYY-MM-DD")
    period_end: str = Field(..., description="YYYY-MM-DD")
    status: str = Field(default="未开始")
    sort_order: int = Field(default=0, ge=0)


class PlanCreate(PlanBase):
    parent_id: int | None = None


class PlanUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    subject_id: int | None = None
    target_minutes: int | None = Field(default=None, ge=0)
    content: str | None = None
    period_start: str | None = None
    period_end: str | None = None
    status: str | None = None
    sort_order: int | None = Field(default=None, ge=0)


class PlanResponse(PlanBase):
    id: int
    parent_id: int | None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class PlanTreeNode(PlanResponse):
    children: list["PlanTreeNode"] = []
    completion_rate: float | None = None
