from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class DeskBase(BaseModel):
    number: str
    location: Optional[str] = None
    coordinates_x: int = 0
    coordinates_y: int = 0
    is_available: bool = True

class DeskCreate(DeskBase):
    pass

class DeskUpdate(BaseModel):
    number: Optional[str] = None
    location: Optional[str] = None
    coordinates_x: Optional[int] = None
    coordinates_y: Optional[int] = None
    is_available: Optional[bool] = None

class Desk(DeskBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int

class ReservationBase(BaseModel):
    desk_id: int
    date: str  # ISO format date

class ReservationCreate(ReservationBase):
    user_id: int

class Reservation(ReservationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    user: Dict[str, Any]  # Basic user info