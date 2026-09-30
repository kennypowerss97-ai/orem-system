import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, func, Time
from sqlalchemy.orm import relationship
from app.database import Base

class Therapist(Base):
    __tablename__ = "therapists"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tc_kimlik = Column(String, unique=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    title = Column(String)
    branch = Column(String, nullable=True)
    phone = Column(String)
    email = Column(String)
    max_weekly_hours = Column(Integer, default=40)
    is_active = Column(Boolean, default=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    specializations = relationship("TherapistSpecialization", back_populates="therapist")
    availability = relationship("TherapistAvailability", back_populates="therapist")

class TherapistSpecialization(Base):
    __tablename__ = "therapist_specializations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    therapist_id = Column(String, ForeignKey("therapists.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("therapy_modules.id"), nullable=False)
    is_primary = Column(Boolean, default=True)
    therapist = relationship("Therapist", back_populates="specializations")

class TherapistAvailability(Base):
    __tablename__ = "therapist_availability"
    id = Column(Integer, primary_key=True, autoincrement=True)
    therapist_id = Column(String, ForeignKey("therapists.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False) # 1-7
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    therapist = relationship("Therapist", back_populates="availability")
