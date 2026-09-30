import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, func, Date
from sqlalchemy.orm import relationship as sa_relationship
from app.database import Base

class Student(Base):
    __tablename__ = "students"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tc_kimlik = Column(String(11), unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(String)
    disability_type = Column(String)
    notes = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    guardians = sa_relationship("Guardian", back_populates="student")
    ram_reports = sa_relationship("RamReport", back_populates="student")

class Guardian(Base):
    __tablename__ = "guardians"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String)
    email = Column(String)
    relationship = Column(String)
    is_primary = Column(Boolean, default=False)
    student = sa_relationship("Student", back_populates="guardians")

class RamReport(Base):
    __tablename__ = "ram_reports"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    report_number = Column(String, nullable=False)
    issuing_ram = Column(String)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    student = sa_relationship("Student", back_populates="ram_reports")
    allocated_modules = sa_relationship("AllocatedModule", back_populates="ram_report")

class AllocatedModule(Base):
    __tablename__ = "allocated_modules"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ram_report_id = Column(String, ForeignKey("ram_reports.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("therapy_modules.id"), nullable=False)
    monthly_individual_hours = Column(Integer, default=8)
    monthly_group_hours = Column(Integer, default=4)
    ram_report = sa_relationship("RamReport", back_populates="allocated_modules")
