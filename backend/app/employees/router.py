from fastapi import APIRouter, HTTPException
from app.employees.schemas import EmployeeCreateSchema, EmployeeUpdateSchema, EmployeeSchema
from app.employees.models import Employee
from app.database import async_session_maker
from sqlalchemy.future import select
from typing import List

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











