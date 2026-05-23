
from sqlalchemy.orm import Mapped,mapped_column

from app.database import Base

class Subject(Base):
    __tablename__='subjects'
    #做关系映射
    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    name:Mapped[str]=mapped_column(unique=True,nullable=False)
    weight:Mapped[float]=mapped_column(default=1.0,nullable=False)
    color:Mapped[str]=mapped_column(nullable=True)
    description:Mapped[str|None]=mapped_column(nullable=True)
    sort_order:Mapped[int]=mapped_column(default=0,nullable=False)
    is_activate:Mapped[int]=mapped_column(default=1,nullable=False)
    created_at: Mapped[str] = mapped_column(nullable=False)
    updated_at: Mapped[str] = mapped_column(nullable=False)
