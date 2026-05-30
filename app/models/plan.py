from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped,mapped_column

from app.database import Base

class Plan(Base):
    __tablename__ = 'plans'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("plans.id", ondelete="CASCADE"), nullable=True
    )
    plan_type: Mapped[str] = mapped_column( nullable=False)
    title: Mapped[str] = mapped_column( nullable=False)
    subject_id: Mapped[int | None] = mapped_column(
        ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=True
    )
    target_minutes: Mapped[int] = mapped_column(default=0, nullable=False)
    content: Mapped[str | None] = mapped_column(nullable=True)
    period_start: Mapped[str] = mapped_column(nullable=False)
    period_end: Mapped[str] = mapped_column( nullable=False)
    status: Mapped[str] = mapped_column(default="未开始", nullable=False)
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[str] = mapped_column(nullable=False)
    updated_at: Mapped[str] = mapped_column( nullable=False)
