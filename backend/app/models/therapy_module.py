from sqlalchemy import Column, String, Boolean, DateTime, Integer, func
from app.database import Base

class TherapyModule(Base):
    __tablename__ = "therapy_modules"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    default_duration_minutes = Column(Integer, default=45)
    is_group_eligible = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
