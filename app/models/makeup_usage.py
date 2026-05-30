from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MakeupUsage(Base):
    __tablename__ = "makeup_usages"
    __table_args__ = (
        UniqueConstraint("user_id", "year_month", name="uq_makeup_user_year_month"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    year_month: Mapped[str] = mapped_column(nullable=False)
    used_count: Mapped[int] = mapped_column(default=0, nullable=False)
    updated_at: Mapped[str] = mapped_column(nullable=False)
