from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(default="user", nullable=False)
    exam_type: Mapped[str] = mapped_column(default="考研", nullable=False)
    target_exam_date: Mapped[str | None] = mapped_column(nullable=True)
    is_active: Mapped[int] = mapped_column(default=1, nullable=False)
    created_at: Mapped[str] = mapped_column(nullable=False)
