from sqlalchemy import select, update
from sqlalchemy.orm import joinedload, selectinload
from app.employees.models import Employee
from app.activities.models import Activity
from app.database import async_session_maker
from app.dao.base import BaseDAO
from app.roles.models import Role
from datetime import datetime, timedelta


class EmployeeDAO(BaseDAO):
    model = Employee

    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .options(
                    selectinload(cls.model.activities).selectinload(Activity.employees),
                    selectinload(cls.model.role).selectinload(Role.activities)
                )
                .filter_by(**filter_by)
            )
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_full_data(cls, employee_id: int):
        async with async_session_maker() as session:
            stmt = (
                select(cls.model)
                .options(
                    selectinload(cls.model.activities).selectinload(Activity.employees),
                    selectinload(cls.model.role)
                )
                .filter_by(id=employee_id)
            )
            result_employee = await session.execute(stmt)
            employee_info = result_employee.unique().scalar_one_or_none()

            if not employee_info:
                return None

            return employee_info

    @classmethod
    async def assign_activities_to_employee(cls, employee_id: int, activity_ids: list[int]):
        async with async_session_maker() as session:
            query_employee = select(Employee).options(selectinload(Employee.activities)).filter_by(id=employee_id)
            result_employee = await session.execute(query_employee)
            employee = result_employee.scalar_one_or_none()
            
            if not employee:
                raise ValueError(f"Сотрудник с ID {employee_id} не найден")
            
            query_activities = select(Activity).filter(Activity.id.in_(activity_ids))
            result_activities = await session.execute(query_activities)
            activities = result_activities.scalars().all()
            
            employee.activities.clear()
            employee.activities.extend(activities)
            
            await session.commit()
            await session.refresh(employee)
            
            return employee

    @classmethod
    async def add_activity_to_employee(cls, employee_id: int, activity_id: int):
        async with async_session_maker() as session:
            query_employee = select(Employee).options(selectinload(Employee.activities)).filter_by(id=employee_id)
            result_employee = await session.execute(query_employee)
            employee = result_employee.scalar_one_or_none()
            
            if not employee:
                raise ValueError(f"Сотрудник с ID {employee_id} не найден")
            
            activity = await session.get(Activity, activity_id)
            if not activity:
                raise ValueError(f"Активность с ID {activity_id} не найдена")
            
            if activity not in employee.activities:
                employee.activities.append(activity)
            
            await session.commit()
            await session.refresh(employee)
            
            return employee

    @classmethod
    async def assign_role_to_employee(cls, employee_id: int, role_id: int):
        async with async_session_maker() as session:
            employee = await session.get(Employee, employee_id)
            if not employee:
                raise ValueError(f"Сотрудник с ID {employee_id} не найден")
            role = await session.get(Role, role_id)
            if not role:
                raise ValueError(f"Роль с ID {role_id} не найдена")
            employee.role_id = role_id
            await session.commit()
            await session.refresh(employee)
            return employee

    @classmethod
    async def get_agent_config_from_db(cls, employee_id: int):
        async with async_session_maker() as session:
            stmt = (
                select(cls.model)
                .options(
                    selectinload(cls.model.activities),
                    selectinload(cls.model.role).selectinload(Role.activities),
                    selectinload(cls.model.server)
                )
                .filter_by(id=employee_id)
            )
            result = await session.execute(stmt)
            employee = result.scalar_one_or_none()
            if not employee:
                return None
            role_activities = set(employee.role.activities if employee.role else [])
            custom_activities = set(employee.activities or [])
            all_activities = list(role_activities | custom_activities)
            config = {
                "employee_id": employee.id,
                "name": employee.name,
                "role": employee.role.name if employee.role else None,
                "os": employee.os,
                "work_start_time": employee.work_start_time.isoformat() if employee.work_start_time else None,
                "work_end_time": employee.work_end_time.isoformat() if employee.work_end_time else None,
                "activity_rate": employee.activity_rate,
                "activities": [
                    {"id": act.id, "name": act.name, "url": act.url, "description": act.description, "os": act.os}
                    for act in all_activities
                ],
                "server_id": employee.server_id,
                "last_heartbeat": employee.last_heartbeat.isoformat() if employee.last_heartbeat else None
            }
            return config
    @classmethod
    async def update_heartbeat_and_status(cls, employee_id: int, status: str, session):
        from datetime import datetime, timedelta
        result = await session.execute(select(Employee).where(Employee.id == employee_id))
        employee = result.scalar_one_or_none()
        now = datetime.now()
        if employee:
            prev_heartbeat = employee.last_heartbeat
            if not prev_heartbeat or (now - prev_heartbeat) < timedelta(seconds=7200):
                agent_status = "online"
            else:
                agent_status = "offline"
            await session.execute(
                update(Employee)
                .where(Employee.id == employee_id)
                .values(last_heartbeat=now, agent_status=agent_status)
            )
            await session.commit()
        

    @classmethod
    async def get_all_activities_for_employee(cls, employee_id: int):
        from sqlalchemy.orm import selectinload
        async with async_session_maker() as session:
            stmt = (
                select(Employee)
                .options(
                    selectinload(Employee.activities),
                    selectinload(Employee.role).selectinload(Role.activities)
                )
                .filter_by(id=employee_id)
            )
            result = await session.execute(stmt)
            employee = result.scalar_one_or_none()
            if not employee:
                return []
            # Eager load activities
            for activity in employee.activities:
                _ = activity.id  # access to ensure loading
            if employee.role:
                for activity in employee.role.activities:
                    _ = activity.id
            role_activities = set(employee.role.activities if employee.role else [])
            custom_activities = set(employee.activities or [])
            all_activities = list(role_activities | custom_activities)
            return all_activities
        
