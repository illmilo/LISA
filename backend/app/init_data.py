import asyncio
from app.database import async_session_maker
from app.roles.models import Role
from app.activities.models import Activity
from sqlalchemy import select

async def main():
    async with async_session_maker() as session:
        activities_data = [
            {"name": "firefox", "url": "duckduckgo.com", "description": "Web browser", "os": "linux"},
            {"name": "libreoffice calc", "url": None, "description": "Spreadsheet", "os": "linux"},
            {"name": "libreoffice writer", "url": None, "description": "Text editor", "os": "linux"},
            {"name": "text editor", "url": None, "description": "Simple text editor", "os": "linux"},
        ]
        activity_objs = {}
        for act in activities_data:
            result = await session.execute(select(Activity).filter_by(name=act["name"]))
            activity = result.scalar_one_or_none()
            if not activity:
                activity = Activity(**act)
                session.add(activity)
                await session.commit()
                await session.refresh(activity)
            activity_objs[act["name"]] = activity

        roles_data = [
            {"name": "admin", "activity_names": ["firefox"]},
            {"name": "user", "activity_names": ["firefox", "libreoffice calc", "libreoffice writer", "text editor"]},
            {"name": "dev", "activity_names": ["firefox", "text editor"]},
        ]
        for role_data in roles_data:
            result = await session.execute(select(Role).filter_by(name=role_data["name"]))
            role = result.scalar_one_or_none()
            activity_ids = [activity_objs[name].id for name in role_data["activity_names"]]
            if not role:
                role = Role(name=role_data["name"], activity_ids=activity_ids)
                session.add(role)
            else:
                role.activity_ids = activity_ids
            await session.commit()

    print("Инициализация завершена!")

if __name__ == "__main__":
    asyncio.run(main()) 