from sqlalchemy import Column, String, Boolean, DateTime, Integer, func
from app.database import Base

class DisabilityType(Base):
    __tablename__ = "disability_types"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
