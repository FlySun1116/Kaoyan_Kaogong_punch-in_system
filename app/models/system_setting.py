
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped,mapped_column

from app.database import Base


class SystemSetting(Base):
    __tablename__ = "system_settings"

    key:Mapped[str]=mapped_column(primary_key=True)
    value:Mapped[str]=mapped_column(nullable=False)
    updated_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    updated_at:Mapped[str]=mapped_column(nullable=False)
