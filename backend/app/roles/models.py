from sqlalchemy import Integer, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base, int_pk, str_uniq

class Role(Base):
    __tablename__ = 'roles'
    id: Mapped[int_pk]
    name: Mapped[str_uniq]
    activity_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=True, default=[])
