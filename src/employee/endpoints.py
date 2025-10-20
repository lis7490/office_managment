from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from datetime import date

from employee.schemas import (
    Employee, EmployeeCreate, EmployeeUpdate, EmployeeDetail,
    Skill, SkillCreate, EmployeeSkill, EmployeeSkillCreate
)
from core.dependencies import get_db_session

router = APIRouter()

@router.get("/", response_model=List[Employee])
async def get_employees(
    skip: int = Query(0, description="Пропустить записи"),
    limit: int = Query(100, description="Лимит записей"),
    position: Optional[str] = Query(None, description="Фильтр по должности"),
    db_session = Depends(get_db_session)
):
    """
    Получить список всех сотрудников
    """
    from employee.models import Employee as EmployeeModel
    
    queryset = EmployeeModel.objects.all()
    
    if position:
        queryset = queryset.filter(position=position)
    
    employees = list(queryset[skip:skip + limit])
    
    result = []
    for emp in employees:
        emp_data = Employee.model_validate(emp)
        # Расчет стажа работы
        emp_data.work_experience_days = emp.get_work_experience_days()
        result.append(emp_data)
    
    return result

@router.post("/", response_model=Employee, status_code=status.HTTP_201_CREATED)
async def create_employee(employee: EmployeeCreate, db_session = Depends(get_db_session)):
    """
    Создать нового сотрудника
    """
    from employee.models import Employee as EmployeeModel, EmployeeSkill as EmployeeSkillModel
    
    try:
        # Создаем сотрудника
        employee_data = employee.model_dump(exclude={'skills'})
        db_employee = EmployeeModel(**employee_data)
        db_employee.save()
        
        # Добавляем навыки если есть
        if employee.skills:
            for skill_data in employee.skills:
                EmployeeSkillModel.objects.create(
                    employee=db_employee,
                    skill_id=skill_data.skill_id,
                    level=skill_data.level
                )
        
        result = Employee.model_validate(db_employee)
        result.work_experience_days = db_employee.get_work_experience_days()
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{employee_id}", response_model=EmployeeDetail)
async def get_employee(employee_id: int, db_session = Depends(get_db_session)):
    """
    Получить сотрудника по ID с детальной информацией
    """
    from employee.models import Employee as EmployeeModel
    
    try:
        employee = EmployeeModel.objects.get(id=employee_id)
        
        # Основные данные
        employee_data = EmployeeDetail.model_validate(employee)
        employee_data.work_experience_days = employee.get_work_experience_days()
        
        # Фотографии
        main_photo = employee.get_main_photo()
        if main_photo:
            employee_data.main_photo = main_photo.image.url
        
        gallery_photos = employee.get_gallery_photos()
        employee_data.gallery_photos = [photo.image.url for photo in gallery_photos]
        
        return employee_data
        
    except EmployeeModel.DoesNotExist:
        raise HTTPException(status_code=404, detail="Employee not found")

@router.put("/{employee_id}", response_model=Employee)
async def update_employee(employee_id: int, employee_data: EmployeeUpdate, db_session = Depends(get_db_session)):
    """
    Обновить сотрудника
    """
    from employee.models import Employee as EmployeeModel
    
    try:
        employee = EmployeeModel.objects.get(id=employee_id)
        
        update_data = employee_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(employee, field, value)
        
        employee.save()
        
        result = Employee.model_validate(employee)
        result.work_experience_days = employee.get_work_experience_days()
        return result
        
    except EmployeeModel.DoesNotExist:
        raise HTTPException(status_code=404, detail="Employee not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{employee_id}")
async def delete_employee(employee_id: int, db_session = Depends(get_db_session)):
    """
    Удалить сотрудника
    """
    from employee.models import Employee as EmployeeModel
    
    try:
        employee = EmployeeModel.objects.get(id=employee_id)
        employee.delete()
        return {"message": "Employee deleted successfully"}
        
    except EmployeeModel.DoesNotExist:
        raise HTTPException(status_code=404, detail="Employee not found")

@router.get("/{employee_id}/skills", response_model=List[EmployeeSkill])
async def get_employee_skills(employee_id: int, db_session = Depends(get_db_session)):
    """
    Получить навыки сотрудника
    """
    from employee.models import EmployeeSkill as EmployeeSkillModel
    
    skills = EmployeeSkillModel.objects.filter(employee_id=employee_id).select_related('skill')
    return [EmployeeSkill.model_validate(skill) for skill in skills]

@router.post("/{employee_id}/skills", response_model=EmployeeSkill)
async def add_employee_skill(employee_id: int, skill_data: EmployeeSkillCreate, db_session = Depends(get_db_session)):
    """
    Добавить навык сотруднику
    """
    from employee.models import EmployeeSkill as EmployeeSkillModel, Employee as EmployeeModel
    
    try:
        employee = EmployeeModel.objects.get(id=employee_id)
        
        skill = EmployeeSkillModel.objects.create(
            employee=employee,
            skill_id=skill_data.skill_id,
            level=skill_data.level
        )
        
        return EmployeeSkill.model_validate(skill)
        
    except EmployeeModel.DoesNotExist:
        raise HTTPException(status_code=404, detail="Employee not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Эндпоинты для навыков
@router.get("/skills/all", response_model=List[Skill])
async def get_all_skills(db_session = Depends(get_db_session)):
    """
    Получить все доступные навыки
    """
    from employee.models import Skill as SkillModel
    
    skills = SkillModel.objects.all()
    return [Skill.model_validate(skill) for skill in skills]

@router.post("/skills/", response_model=Skill, status_code=status.HTTP_201_CREATED)
async def create_skill(skill: SkillCreate, db_session = Depends(get_db_session)):
    """
    Создать новый навык
    """
    from employee.models import Skill as SkillModel
    
    db_skill = SkillModel.objects.create(**skill.model_dump())
    return Skill.model_validate(db_skill)