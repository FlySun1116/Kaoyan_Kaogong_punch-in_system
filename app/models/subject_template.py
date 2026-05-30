from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SubjectTemplate(Base):
    __tablename__ = "subject_templates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    exam_type: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    default_weight: Mapped[float] = mapped_column(default=1.0, nullable=False)
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)
    is_active: Mapped[int] = mapped_column(default=1, nullable=False)
    created_at: Mapped[str] = mapped_column(nullable=False)
