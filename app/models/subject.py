
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column

from app.database import Base

class Subject(Base):
    __tablename__='subjects'
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_subject_user_name"),
    )

    #做关系映射
    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name:Mapped[str]=mapped_column(nullable=False)
    weight:Mapped[float]=mapped_column(default=1.0,nullable=False)
    color: Mapped[str | None] = mapped_column(nullable=True)
    description:Mapped[str|None]=mapped_column(nullable=True)
    sort_order:Mapped[int]=mapped_column(default=0,nullable=False)
    is_activate:Mapped[int]=mapped_column(default=1,nullable=False)
    created_at: Mapped[str] = mapped_column(nullable=False)
    updated_at: Mapped[str] = mapped_column(nullable=False)
