from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from app.database import Base, int_pk, str_uniq

role_activity = Table(
    'role_activity',
    Base.metadata,
    Column('role_id', ForeignKey('roles.id'), primary_key=True),
    Column('activity_id', ForeignKey('activitys.id'), primary_key=True)
)

class Role(Base):
    __tablename__ = 'roles'
    id: Mapped[int_pk]
    name: Mapped[str_uniq]
    activities: Mapped[list["Activity"]] = relationship("Activity", secondary=role_activity, back_populates="roles")
    employees: Mapped[list["Employee"]] = relationship("Employee", back_populates="role")
