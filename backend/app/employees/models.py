from sqlalchemy import ForeignKey, Text, Time, Float, DateTime, Integer, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base, int_pk

class Employee(Base):
    id: Mapped[int_pk]
    name: Mapped[str]
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'), nullable=True)
    activity_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=True, default=[])
    os: Mapped[str]
    work_start_time = mapped_column(Time, nullable=True)
    work_end_time = mapped_column(Time, nullable=True)
    activity_rate = mapped_column(Float, nullable=True)
    server_id: Mapped[int] = mapped_column(ForeignKey('servers.id'), default=1)
    last_heartbeat = mapped_column(DateTime, nullable=True, default=None)
    agent_status = mapped_column(Text, nullable=True)

    def __str__(self):
        return (f"{self.__class__.__name__}(id={self.id}, "
                f"name={self.name!r},"
                f"role_id={self.role_id!r},"
                f"os={self.os!r},"
                f"activity_ids={self.activity_ids!r},"
                f"server_id={self.server_id!r})")

    def __repr__(self):
        return str(self)
    
    def to_dict(self): 
        return {
            "id": self.id,
            "name": self.name,
            "role_id": self.role_id,
            "os": self.os,
            "activity_ids": self.activity_ids or [],
            "work_start_time": self.work_start_time.isoformat() if self.work_start_time else None,
            "work_end_time": self.work_end_time.isoformat() if self.work_end_time else None,
            "activity_rate": self.activity_rate,
            "server_id": self.server_id,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "agent_status": self.agent_status,
        }


