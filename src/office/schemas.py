from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class OfficeBase(BaseModel):
    name: str
    address: str
    city: str
    capacity: int
    description: Optional[str] = None

class OfficeCreate(OfficeBase):
    pass

class OfficeUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    capacity: Optional[int] = None
    description: Optional[str] = None

class Office(OfficeBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None