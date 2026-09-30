from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class EducationProgram(Base):
    __tablename__ = "education_programs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    code = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    color = Column(String, default="#1890ff")
    default_individual_hours = Column(Integer, default=8)
    default_group_hours = Column(Integer, default=4)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    modules = relationship("EducationProgramModule", back_populates="program", cascade="all, delete-orphan")

class EducationProgramModule(Base):
    __tablename__ = "education_program_modules"
    id = Column(Integer, primary_key=True, autoincrement=True)
    program_id = Column(Integer, ForeignKey("education_programs.id"), nullable=False)
    name = Column(String, nullable=False)
    code = Column(String, nullable=True)
    description = Column(String, nullable=True)
    is_group_eligible = Column(Boolean, default=True)
    duration_minutes = Column(Integer, default=45)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    program = relationship("EducationProgram", back_populates="modules")
