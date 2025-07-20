from fastapi import APIRouter, HTTPException
from app.roles.schemas import RoleCreateSchema, RoleUpdateSchema, RoleSchema, RoleNameSchema
from app.roles.models import Role
from app.database import async_session_maker
from sqlalchemy.future import select
from typing import List
from app.activities.models import Activity
from app.activities.schemas import ActivitySchema
from sqlalchemy import select

router_roles = APIRouter(prefix='/roles', tags=['Роли'])

@router_roles.post('/')
async def create_role(role: RoleCreateSchema):
    async with async_session_maker() as session:
        db_role = Role(**role.model_dump())
        session.add(db_role)
        await session.commit()
    return {"message": "Роль успешно создана"}

@router_roles.get('/', response_model=List[RoleSchema])
async def get_all_roles():
    async with async_session_maker() as session:
        result = await session.execute(select(Role))
        return result.scalars().all()

@router_roles.get('/{role_id}', response_model=RoleSchema)
async def get_role(role_id: int):
    async with async_session_maker() as session:
        role = await session.get(Role, role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Роль не найдена")
        return role

@router_roles.put('/{role_id}', response_model=RoleSchema)
async def update_role(role_id: int, role_data: RoleUpdateSchema):
    async with async_session_maker() as session:
        role = await session.get(Role, role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Роль не найдена")
        for field, value in role_data.model_dump(exclude_unset=True).items():
            setattr(role, field, value)
        await session.commit()
        await session.refresh(role)
        return role

@router_roles.delete('/{role_id}')
async def delete_role(role_id: int):
    async with async_session_maker() as session:
        role = await session.get(Role, role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Роль не найдена")
        await session.delete(role)
        await session.commit()
    return {"message": "Роль удалена"}

@router_roles.post('/{role_id}/add-activity/{activity_id}', summary='Назначить активность роли')
async def add_activity_to_role(role_id: int, activity_id: int):
    async with async_session_maker() as session:
        role = await session.get(Role, role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Роль не найдена")
        if role.activity_ids is None:
            role.activity_ids = []
        if activity_id not in role.activity_ids:
            role.activity_ids.append(activity_id)
        await session.commit()
        await session.refresh(role)
    return {"message": "Активность добавлена к роли"}

@router_roles.post('/{role_id}/remove-activity/{activity_id}', summary='Удалить активность у роли')
async def remove_activity_from_role(role_id: int, activity_id: int):
    async with async_session_maker() as session:
        role = await session.get(Role, role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Роль не найдена")
        if role.activity_ids and activity_id in role.activity_ids:
            role.activity_ids.remove(activity_id)
        await session.commit()
        await session.refresh(role)
    return {"message": "Активность удалена у роли"}

@router_roles.get('/{role_id}/activities')
async def get_role_activities(role_id: int):
    async with async_session_maker() as session:
        role = await session.get(Role, role_id)
        if not role:
            raise HTTPException(status_code=404, detail='Роль не найдена')
        if not role.activity_ids:
            return []
        result = await session.execute(select(Activity).where(Activity.id.in_(role.activity_ids)))
        activities = result.scalars().all()
        return [ActivitySchema.model_validate(a, from_attributes=True) for a in activities]
