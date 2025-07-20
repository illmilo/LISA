from sqlalchemy.orm import selectinload
from app.activities.models import Activity
from app.employees.models import Employee
from sqlalchemy import select
from app.database import async_session_maker
from app.dao.base import BaseDAO


class ActivityDAO(BaseDAO):
    model = Activity

    @classmethod
    async def find_full_data(cls, activity_id: int):
        async with async_session_maker() as session:
            query_activity = select(cls.model).filter_by(id=activity_id)
            result_activity = await session.execute(query_activity)
            activity_info = result_activity.unique().scalar_one_or_none()

            if not activity_info:
                return None

            # Сериализация внутри сессии!
            return activity_info.to_dict()

    @classmethod
    async def find_with_employees(cls, activity_id: int):
        async with async_session_maker() as session:
            query_activity = select(cls.model).filter_by(id=activity_id)
            result_activity = await session.execute(query_activity)
            activity_info = result_activity.scalar_one_or_none()

            if not activity_info:
                return None

            activity_data = activity_info.to_dict()
            activity_data['employees'] = [employee.to_dict() for employee in activity_info.employees] if activity_info.employees else list()

            return activity_data 