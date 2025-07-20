from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base, str_uniq, int_pk, str_null_true
from sqlalchemy import select
from app.database import async_session_maker
import asyncio

class Activity(Base):
    __tablename__ = "activities"
    
    id: Mapped[int_pk]
    name: Mapped[str]
    url: Mapped[str_null_true]
    description: Mapped[str]
    os: Mapped[str]

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name!r}, url={self.url!r}, os={self.os!r})"

    def __repr__(self):
        return str(self)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "description": self.description,
            "os": self.os
        }
