from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from core.database import Base

class Office(Base):
    __tablename__ = "offices"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    address = Column(String(200), nullable=False)
    city = Column(String(50), nullable=False)
    capacity = Column(Integer, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())