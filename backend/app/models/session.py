import uuid
import enum
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, func, Date, Time, Enum
from sqlalchemy.orm import relationship
from app.database import Base

class SessionTypeEnum(str, enum.Enum):
    INDIVIDUAL = "INDIVIDUAL"
    GROUP = "GROUP"
    MAKEUP = "MAKEUP"

class SessionStatusEnum(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    STUDENT_ABSENT = "STUDENT_ABSENT"
    THERAPIST_ABSENT = "THERAPIST_ABSENT"
    CANCELLED = "CANCELLED"

class TherapySession(Base):
    __tablename__ = "therapy_sessions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    module_id = Column(Integer, ForeignKey("therapy_modules.id"), nullable=False)
    therapist_id = Column(String, ForeignKey("therapists.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    session_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    session_type = Column(Enum(SessionTypeEnum), default=SessionTypeEnum.INDIVIDUAL)
    status = Column(Enum(SessionStatusEnum), default=SessionStatusEnum.SCHEDULED)
    cancellation_reason = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    participants = relationship("SessionParticipant", back_populates="session")

class SessionParticipant(Base):
    __tablename__ = "session_participants"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("therapy_sessions.id"), nullable=False)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    attended = Column(Boolean, default=False)
    absence_reason = Column(String, nullable=True)
    is_telafi_eligible = Column(Boolean, default=False)
    
    session = relationship("TherapySession", back_populates="participants")
