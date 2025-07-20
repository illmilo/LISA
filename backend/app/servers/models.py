from sqlalchemy import ForeignKey, text, Text, Table, Column, Time, Float, Integer, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base, str_uniq, int_pk, str_null_true



class Server(Base):
    id: Mapped[int_pk]
    name: Mapped[str]
    password: Mapped[str]
    server_key: Mapped[str]
    employee_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=True, default=[])

def __str__(self):
    return (f"{self.__class__.__name__}(id={self.id}, "
            f"name={self.name!r},"
            f"password={self.password!r},"
            f"server_key={self.server_key!r})")


def __repr__(self):
    return str(self)

def to_dict(self):
    return {
        "id": self.id,
        "name": self.name,
        "password": self.password,
        "server_key": self.server_key,
        "employee_ids": self.employee_ids or []
    }

