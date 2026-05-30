from pydantic import BaseModel, Field


class SubjectBase(BaseModel):
    """创建和更新共用的字段"""

    name: str = Field(..., min_length=1, max_length=50, description="科目名称")
    weight: float = Field(default=1.0, ge=0.1, le=10.0, description="权重")
    color: str | None = Field(default=None, max_length=20)
    description: str | None = Field(default=None, max_length=500)
    sort_order: int = Field(default=0, ge=0)


class SubjectCreate(SubjectBase):
    """创建科目时用的模型"""

    pass


class SubjectUpdate(BaseModel):
    """更新科目：字段都可空，只改传了的"""

    name: str | None = Field(default=None, min_length=1, max_length=50)
    weight: float | None = Field(default=None, ge=0.1, le=10.0)
    color: str | None = None
    description: str | None = None
    sort_order: int | None = Field(default=None, ge=0)
    is_activate: int | None = Field(default=None, ge=0, le=1)


class SubjectResponse(SubjectBase):
    """返回给前端的模型"""

    id: int
    is_activate: int
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}
