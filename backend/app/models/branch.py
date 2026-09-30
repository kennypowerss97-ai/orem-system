from sqlalchemy import Column, String, Boolean, DateTime, Integer, func
from app.database import Base

class TeacherBranch(Base):
    __tablename__ = "teacher_branches"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    code = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    color = Column(String, default="#1890ff")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
