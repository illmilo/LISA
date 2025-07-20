from app.database import async_session_maker
from sqlalchemy import select
from app.roles.models import Role
from app.activities.models import Activity
from app.roles.schemas import RoleSchema
from sqlalchemy.orm import selectinload
from app.activities.schemas import ActivitySchema, ActivityShallowSchema
from app.dao.base import BaseDAO

class RoleDAO(BaseDAO):
    model = Role

    @classmethod
    async def find_all(cls, **filter_by) -> list[RoleSchema]:
        async with async_session_maker() as session:
            stmt = select(cls.model).options(selectinload(cls.model.activities)).filter_by(**filter_by)
            result = await session.execute(stmt)
            return result.scalars().all()

    @classmethod
    async def get_all(cls):
        async with async_session_maker() as session:
            stmt = select(Role).options(selectinload(Role.activities))
            result = await session.execute(stmt)
            roles = result.scalars().all()
            return [
                RoleSchema.model_validate({
                    "id": role.id,
                    "name": role.name,
                    "activities": [ActivityShallowSchema.model_validate(a, from_attributes=True) for a in role.activities]
                }) for role in roles
            ]

    @classmethod
    async def get_by_id(cls, role_id: int):
        async with async_session_maker() as session:
            stmt = select(Role).filter_by(id=role_id)
            result = await session.execute(stmt)
            role = result.scalar_one_or_none()
            if not role:
                return None
            return RoleSchema.model_validate({
                "id": role.id,
                "name": role.name,
                "activities": [ActivityShallowSchema.model_validate(a, from_attributes=True) for a in role.activities]
            })

    @classmethod
    async def create(cls, name: str):
        async with async_session_maker() as session:
            role = Role(name=name)
            session.add(role)
            await session.commit()
            await session.refresh(role)
            return role

    @classmethod
    async def update(cls, role_id: int, name: str):
        async with async_session_maker() as session:
            role = await session.get(Role, role_id)
            if not role:
                return None
            role.name = name
            await session.commit()
            await session.refresh(role)
            return role

    @classmethod
    async def delete(cls, role_id: int):
        async with async_session_maker() as session:
            role = await session.get(Role, role_id)
            if not role:
                return False
            await session.delete(role)
            await session.commit()
            return True

    @classmethod
    async def set_activities(cls, role_id: int, activity_ids: list[int]):
        async with async_session_maker() as session:
            stmt = select(Role).filter_by(id=role_id)
            result = await session.execute(stmt)
            role = result.scalar_one_or_none()
            if not role:
                return None
            activities = (await session.execute(select(Activity).where(Activity.id.in_(activity_ids)))).scalars().all()
            role.activities = activities
            await session.commit()
            await session.refresh(role)
            # Повторно получить роль с подгруженными activities
            result = await session.execute(stmt)
            role = result.scalar_one_or_none()
            data = {
                "id": role.id,
                "name": role.name,
                "activities": [a.id for a in role.activities]
            }
            return RoleSchema.model_validate(data)
