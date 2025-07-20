import asyncio
from app.database import async_session_maker
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.employees.models import Employee
from app.roles.models import Role
from app.activities.models import Activity
from app.servers.models import Server

async def main():
    async with async_session_maker() as session:
        # Роли
        roles = ["admin", "user", "dev"]
        role_objs = {}
        for role_name in roles:
            result = await session.execute(select(Role).filter_by(name=role_name))
            role_obj = result.scalar_one_or_none()
            if not role_obj:
                role_obj = Role(name=role_name)
                session.add(role_obj)
                await session.commit()
                await session.refresh(role_obj)
            role_objs[role_name] = role_obj

        activities = [
            {"name": "firefox", "url": "duckduckgo.com", "description": "Web browser", "os": "linux"},
            {"name": "libreoffice calc", "url": None, "description": "Spreadsheet", "os": "linux"},
            {"name": "libreoffice writer", "url": None, "description": "Text editor", "os": "linux"},
            {"name": "text editor", "url": None, "description": "Simple text editor", "os": "linux"},
        ]
        activity_objs = {}
        for act in activities:
            result = await session.execute(select(Activity).filter_by(name=act["name"]))
            activity_obj = result.scalar_one_or_none()
            if not activity_obj:
                activity_obj = Activity(**act)
                session.add(activity_obj)
                await session.commit()
                await session.refresh(activity_obj)
            activity_objs[act["name"]] = activity_obj

        user_role = (await session.execute(
            select(Role).options(selectinload(Role.activities)).filter_by(name="user")
        )).scalar_one_or_none()
        admin_role = (await session.execute(
            select(Role).options(selectinload(Role.activities)).filter_by(name="admin")
        )).scalar_one_or_none()
        dev_role = (await session.execute(
            select(Role).options(selectinload(Role.activities)).filter_by(name="dev")
        )).scalar_one_or_none()

        user_role.activities = [
            activity_objs["firefox"],
            activity_objs["libreoffice calc"],
            activity_objs["libreoffice writer"],
            activity_objs["text editor"]
        ]
        admin_role.activities = [activity_objs["firefox"]]
        dev_role.activities = [activity_objs["firefox"], activity_objs["text editor"]]
        await session.commit()

if __name__ == "__main__":
    asyncio.run(main()) 