
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Backup(Base):
    __tablename__ = "backups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(nullable=False)
    file_path: Mapped[str] = mapped_column(nullable=False)
    file_size: Mapped[str] = mapped_column(nullable=False)
    backup_type: Mapped[str] = mapped_column(default="manual", nullable=False)
    created_at: Mapped[str] = mapped_column(nullable=False)