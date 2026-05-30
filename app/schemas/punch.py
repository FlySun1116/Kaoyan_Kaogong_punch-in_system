from pydantic import BaseModel, Field


class PunchBase(BaseModel):
    punch_date: str = Field(..., description="YYYY-MM-DD")
    subject_id: int
    actual_minutes: int = Field(..., ge=0)
    content: str | None = None


class PunchCreate(PunchBase):
    pass


class PunchUpdate(BaseModel):
    actual_minutes: int | None = Field(default=None, ge=0)
    content: str | None = None


class PunchResponse(PunchBase):
    id: int
    is_makeup: int
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class PunchBatchCreate(BaseModel):
    records: list[PunchCreate] = Field(..., min_length=1)
