from fastapi import APIRouter, Depends, HTTPException, Body
from app.employees.models import Employee
from app.activities.models import Activity
from app.database import async_session_maker
from sqlalchemy import select
from app.employees.dao import EmployeeDAO
from app.employees.rb import RBEmp
from app.employees.schemas import EmployeeSchema, EmployeeCreateSchema, EmployeeUpdateSchema, EmployeeSchemaWnoActivities
from typing import List
import json 
import os
import shutil
from app.servers.dao import ServerDAO
from app.servers.schemas import ServerSchema
from datetime import datetime, timedelta

router_employees = APIRouter(prefix = '/agents', tags = ['Работа с агентами'])

@router_employees.get("/", summary = 'Получить всех агентов')
async def get_all_employees(request_body: RBEmp = Depends()) -> list[EmployeeSchemaWnoActivities]:
    employees = await EmployeeDAO.find_all(**request_body.to_dict())
    return employees

@router_employees.get("/{employee_id}", summary = 'Получить агента по ID')
async def get_employee_by_id(employee_id: int) -> EmployeeSchema | dict:
    employee = await EmployeeDAO.find_full_data(employee_id)
    if not employee:
        return {"error": "Агент c ID " + str(employee_id) + " не найден"}
    return employee

@router_employees.get("/by_filter", summary = 'Получить агента по фильтру')
async def get_employee_by_filter(request_body: RBEmp = Depends()) -> EmployeeSchema | dict:
    employee = await EmployeeDAO.find_one_or_none(**request_body.to_dict())
    if not employee:
        return {"error": "Агент не найден"}
    return employee

@router_employees.post("/", summary = 'Создать нового агента')
async def create_employee(employee_data: EmployeeCreateSchema):
    async with async_session_maker() as session:
        employee_dict = {
            "name": employee_data.name,
            "role_id": employee_data.role_id,
            "os": employee_data.os.value,
            "work_start_time": employee_data.work_start_time,
            "work_end_time": employee_data.work_end_time,
            "activity_rate": employee_data.activity_rate,
            "server_id": employee_data.server_id,
            "last_heartbeat": employee_data.last_heartbeat
        }
        new_employee = Employee(**employee_dict)
        session.add(new_employee)
        await session.commit()
        await session.refresh(new_employee)
        return new_employee

@router_employees.put("/{employee_id}", summary = 'Обновить агента')
async def update_employee(employee_id: int, employee_data: EmployeeUpdateSchema):
    async with async_session_maker() as session:
        employee = await session.get(Employee, employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail=f"Агент с ID {employee_id} не найден")
        update_data = employee_data.model_dump(exclude_unset=True)
        if 'role_id' in update_data:
            setattr(employee, 'role_id', update_data['role_id'])
            update_data.pop('role_id')
        if 'os' in update_data:
            update_data['os'] = update_data['os'].value
        for field, value in update_data.items():
            setattr(employee, field, value)
        await session.commit()
        await session.refresh(employee)
        return employee

@router_employees.delete("/{employee_id}", summary = 'Удалить агента')
async def delete_employee(employee_id: int):
    async with async_session_maker() as session:
        employee = await session.get(Employee, employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail=f"Агент с ID {employee_id} не найден")
        
        await session.delete(employee)
        await session.commit()
        return {"message": f"Агент с ID {employee_id} удален"}

@router_employees.post("/{employee_id}/assign_activities", summary = 'Назначить активности агенту')
async def assign_activities_to_employee(employee_id: int, activity_ids: List[int]):
    try:
        employee = await EmployeeDAO.assign_activities_to_employee(employee_id, activity_ids)
        return {"message": f"Активности {activity_ids} назначены агенту {employee_id}", "employee": employee}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router_employees.post("/{employee_id}/add_activity/{activity_id}", summary = 'Добавить активность агенту')
async def add_activity_to_employee(employee_id: int, activity_id: int):
    try:
        employee = await EmployeeDAO.add_activity_to_employee(employee_id, activity_id)
        return {"message": f"Активность {activity_id} добавлена агенту {employee_id}", "employee": employee}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    

@router_employees.post("/{employee_id}/start_agent", summary="Запустить linux-агента")
async def start_agent(employee_id: int):
    config = await EmployeeDAO.get_agent_config_from_db(employee_id)
    if not config:
        raise HTTPException(status_code=404, detail="Агент не найден")

    base_dir = "/home/lisoon/Documents/23/created_agents" 
    template_dir = "/home/lisoon/Documents/23/LISA/agent/agent_linux"
    agent_dir = os.path.join(base_dir, f"agent_linux_{employee_id}")

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

    import subprocess

    main_script_path = os.path.join(agent_dir, "mainScript.sh")
    if not os.path.isfile(main_script_path):
        raise HTTPException(status_code=500, detail="mainScript.sh не найден в папке агента")

    try:
        subprocess.Popen(["bash", main_script_path], cwd=agent_dir)
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

@router_employees.get("/{employee_id}/all_activities", summary="Получить все активности агента (роль + индивидуальные)")
async def get_all_activities(employee_id: int):
    activities = await EmployeeDAO.get_all_activities_for_employee(employee_id)
    return {"activities": [a.to_dict() for a in activities]}

@router_employees.post("/{employee_id}/assign_role/{role_id}", summary="Назначить роль агенту")
async def assign_role_to_employee(employee_id: int, role_id: int):
    try:
        employee = await EmployeeDAO.assign_role_to_employee(employee_id, role_id)
        return {"message": f"Роль {role_id} назначена агенту {employee_id}", "employee": employee}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))











