from fastapi import APIRouter, HTTPException
from app.servers.schemas import ServerCreateSchema, ServerUpdateSchema, ServerSchema
from app.servers.models import Server
from app.database import async_session_maker
from sqlalchemy.future import select
from typing import List

router_servers = APIRouter(prefix='/servers', tags=['Работа с серверами'])

@router_servers.post("/", summary='Создать сервер')
async def create_server(server_data: ServerCreateSchema):
    async with async_session_maker() as session:
        new_server = Server(**server_data.model_dump())
        session.add(new_server)
        await session.commit()
    return {"message": "Сервер успешно создан"}

@router_servers.get("/", response_model=List[ServerSchema], summary='Получить все сервера')
async def get_all_servers():
    async with async_session_maker() as session:
        result = await session.execute(select(Server))
        return result.scalars().all()

@router_servers.get("/{server_id}", response_model=ServerSchema, summary='Получить сервер по ID')
async def get_server_by_id(server_id: int):
    async with async_session_maker() as session:
        server = await session.get(Server, server_id)
        if not server:
            raise HTTPException(status_code=404, detail="Сервер не найден")
        return server

@router_servers.put("/{server_id}", response_model=ServerSchema, summary='Обновить сервер')
async def update_server(server_id: int, server_data: ServerUpdateSchema):
    async with async_session_maker() as session:
        server = await session.get(Server, server_id)
        if not server:
            raise HTTPException(status_code=404, detail="Сервер не найден")
        for field, value in server_data.model_dump(exclude_unset=True).items():
            setattr(server, field, value)
        await session.commit()
        await session.refresh(server)
        return server

@router_servers.delete("/{server_id}", summary='Удалить сервер')
async def delete_server(server_id: int):
    async with async_session_maker() as session:
        server = await session.get(Server, server_id)
        if not server:
            raise HTTPException(status_code=404, detail="Сервер не найден")
        await session.delete(server)
        await session.commit()
    return {"message": "Сервер удалён"}

@router_servers.post('/{server_id}/add-employee/{employee_id}', summary='Добавить сотрудника на сервер')
async def add_employee_to_server(server_id: int, employee_id: int):
    async with async_session_maker() as session:
        server = await session.get(Server, server_id)
        if not server:
            raise HTTPException(status_code=404, detail="Сервер не найден")
        from app.employees.models import Employee
        employee = await session.get(Employee, employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Сотрудник не найден")
        if server.employee_ids is None:
            server.employee_ids = []
        if employee_id not in server.employee_ids:
            server.employee_ids.append(employee_id)
        employee.server_id = server_id
        await session.commit()
        await session.refresh(server)
    return {"message": "Сотрудник добавлен на сервер"}

@router_servers.post('/{server_id}/remove-employee/{employee_id}', summary='Удалить сотрудника с сервера')
async def remove_employee_from_server(server_id: int, employee_id: int):
    async with async_session_maker() as session:
        server = await session.get(Server, server_id)
        if not server:
            raise HTTPException(status_code=404, detail="Сервер не найден")
        from app.employees.models import Employee
        employee = await session.get(Employee, employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Сотрудник не найден")
        if server.employee_ids and employee_id in server.employee_ids:
            server.employee_ids.remove(employee_id)
        if employee.server_id == server_id:
            employee.server_id = None
        await session.commit()
        await session.refresh(server)
    return {"message": "Сотрудник удалён с сервера"}
