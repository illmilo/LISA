import os
import shutil
import json
import subprocess
from fastapi import APIRouter, HTTPException, Body
from app.employees.schemas import EmployeeCreateSchema, EmployeeUpdateSchema, EmployeeSchema
from app.employees.models import Employee
from app.database import async_session_maker
from sqlalchemy.future import select
from typing import List
from app.employees.dao import EmployeeDAO
from datetime import datetime
from app.config import AGENT_TEMPLATE_DIR, BASE_AGENT_DIR

router_employees = APIRouter(prefix='/agents', tags=['Работа с агентами'])

@router_employees.post("/", summary='Создать нового агента')
async def create_employee(employee_data: EmployeeCreateSchema):
    async with async_session_maker() as session:
        new_employee = Employee(**employee_data.model_dump())
        session.add(new_employee)
        await session.commit()
    return {"message": "Агент успешно создан"}

@router_employees.get("/", response_model=List[EmployeeSchema], summary='Получить всех агентов')
async def get_all_employees():
    async with async_session_maker() as session:
        result = await session.execute(select(Employee))
        return result.scalars().all()

@router_employees.get("/{employee_id}", response_model=EmployeeSchema, summary='Получить агента по ID')
async def get_employee_by_id(employee_id: int):
    async with async_session_maker() as session:
        employee = await session.get(Employee, employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Агент не найден")
        return employee

@router_employees.put("/{employee_id}", response_model=EmployeeSchema, summary='Обновить агента')
async def update_employee(employee_id: int, employee_data: EmployeeUpdateSchema):
    async with async_session_maker() as session:
        employee = await session.get(Employee, employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Агент не найден")
        for field, value in employee_data.model_dump(exclude_unset=True).items():
            setattr(employee, field, value)
        await session.commit()
        await session.refresh(employee)
        return employee

@router_employees.delete("/{employee_id}", summary='Удалить агента')
async def delete_employee(employee_id: int):
    async with async_session_maker() as session:
        employee = await session.get(Employee, employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Агент не найден")
        await session.delete(employee)
        await session.commit()
    return {"message": "Агент удалён"}

@router_employees.post('/{employee_id}/add-activity/{activity_id}', summary='Назначить активность агенту')
async def add_activity_to_employee(employee_id: int, activity_id: int):
    async with async_session_maker() as session:
        employee = await session.get(Employee, employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Агент не найден")
        if employee.activity_ids is None:
            employee.activity_ids = []
        if activity_id not in employee.activity_ids:
            employee.activity_ids.append(activity_id)
        await session.commit()
        await session.refresh(employee)
    return {"message": "Активность добавлена агенту"}

@router_employees.post('/{employee_id}/remove-activity/{activity_id}', summary='Удалить активность у агента')
async def remove_activity_from_employee(employee_id: int, activity_id: int):
    async with async_session_maker() as session:
        employee = await session.get(Employee, employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Агент не найден")
        if employee.activity_ids and activity_id in employee.activity_ids:
            employee.activity_ids.remove(activity_id)
        await session.commit()
        await session.refresh(employee)
    return {"message": "Активность удалена у агента"}

@router_employees.post("/{employee_id}/start_agent", summary="Запустить linux-агента")
async def start_agent(employee_id: int):
    config = await EmployeeDAO.get_agent_config_from_db(employee_id)
    if not config:
        raise HTTPException(status_code=404, detail="Агент не найден")

    agent_dir = os.path.join(BASE_AGENT_DIR, f"agent_linux_{employee_id}")
    template_dir = AGENT_TEMPLATE_DIR

    if os.path.exists(agent_dir):
        shutil.rmtree(agent_dir)
    shutil.copytree(template_dir, agent_dir)

    config_path = os.path.join(agent_dir, "agent_config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    server_id = config.get("server_id")
    if server_id:
        from app.servers.dao import ServerDAO
        from app.servers.schemas import ServerSchema
        server = await ServerDAO.get_server_by_id(server_id)
        if server:
            server_config = ServerSchema.model_validate(server, from_attributes=True).model_dump()
            server_config_path = os.path.join(agent_dir, "server_config.json")
            with open(server_config_path, "w") as f:
                json.dump(server_config, f, indent=2)

    main_script_path = os.path.join(agent_dir, "mainScript.sh")
    if not os.path.isfile(main_script_path):
        raise HTTPException(status_code=500, detail="mainScript.sh не найден в папке агента")

    import asyncio
    try:
        _ = await asyncio.create_subprocess_exec(
            "bash", main_script_path,
            cwd=agent_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка запуска MainScript.sh: {e}")

    return {"status": "ok", "agent_dir": agent_dir, "config_path": config_path}


@router_employees.post("/{employee_id}/stop_agent", summary="Остановить linux-агента")
async def stop_agent(employee_id: int):
    pass  # дальше докер останавливает агента


@router_employees.post("/{employee_id}/heartbeat", summary="Приём heartbeat от агента")
async def agent_heartbeat(employee_id: int, status: str = Body(...)):
    async with async_session_maker() as session:
        await EmployeeDAO.update_heartbeat_and_status(employee_id, status, session)
    return {"status": "heartbeat received"}













