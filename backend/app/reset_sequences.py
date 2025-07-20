import asyncio
from app.database import async_session_maker
from sqlalchemy import text

async def reset_sequences():
    async with async_session_maker() as session:
        # Сброс счетчиков для всех таблиц
        sequences = [
            "employees_id_seq",
            "roles_id_seq", 
            "activities_id_seq",
            "servers_id_seq"
        ]
        
        for seq in sequences:
            await session.execute(text(f"ALTER SEQUENCE {seq} RESTART WITH 1"))
        
        await session.commit()
        print("Счетчики автоинкремента сброшены!")

if __name__ == "__main__":
    asyncio.run(reset_sequences()) 