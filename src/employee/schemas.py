from pydantic import BaseModel, ConfigDict, validator
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from enum import Enum

class PositionEnum(str, Enum):
    BACKEND = "backend"
    FRONTEND = "frontend" 
    TESTER = "tester"
    MANAGER = "manager"
    DESIGNER = "designer"

class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"

class SkillLevelEnum(int, Enum):
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4

class SkillBase(BaseModel):
    name: str

class SkillCreate(SkillBase):
    pass

class Skill(SkillBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int

class EmployeeSkillBase(BaseModel):
    skill_id: int
    level: SkillLevelEnum

class EmployeeSkillCreate(EmployeeSkillBase):
    pass

class EmployeeSkill(EmployeeSkillBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    skill: Skill

class EmployeeImageBase(BaseModel):
    image: str  # URL пути к изображению

class EmployeeImage(EmployeeImageBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    uploaded_at: datetime

class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    position: PositionEnum
    desk_number: int
    hire_date: date
    gender: GenderEnum

class EmployeeCreate(EmployeeBase):
    skills: Optional[List[EmployeeSkillCreate]] = []

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    position: Optional[PositionEnum] = None
    desk_number: Optional[int] = None
    gender: Optional[GenderEnum] = None

class Employee(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    work_experience_days: int
    skills: List[EmployeeSkill] = []
    images: List[EmployeeImage] = []
    
    @validator('work_experience_days', pre=True, always=True)
    def calculate_experience(cls, v, values):
        if isinstance(v, int):
            return v
        # Расчет будет сделан в эндпоинте
        return 0

class EmployeeDetail(Employee):
    main_photo: Optional[str] = None
    gallery_photos: List[str] = []