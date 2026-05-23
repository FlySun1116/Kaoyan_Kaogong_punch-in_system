from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PunchRecord(Base):
    __tablename__ = "punch_records"
    __table_args__ = (
        UniqueConstraint("punch_date", "subject_id", name="uq_punch_date_subject"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    punch_date: Mapped[str] = mapped_column(nullable=False)
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False
    )
    actual_minutes: Mapped[int] = mapped_column(default=0, nullable=False)
    content: Mapped[str | None] = mapped_column( nullable=True)
    is_makeup: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[str] = mapped_column(nullable=False)
    updated_at: Mapped[str] = mapped_column(nullable=False)