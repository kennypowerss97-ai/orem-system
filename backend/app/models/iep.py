import uuid
import enum
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, func, Date, Float, Enum
from sqlalchemy.orm import relationship
from app.database import Base

class GoalStatusEnum(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    ACQUIRED = "ACQUIRED"
    MAINTAINED = "MAINTAINED"

class IepPlan(Base):
    __tablename__ = "iep_plans"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("therapy_modules.id"), nullable=False)
    coordinator_therapist_id = Column(String, ForeignKey("therapists.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    notes = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    goals = relationship("IepGoal", back_populates="plan")

class IepGoal(Base):
    __tablename__ = "iep_goals"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    iep_plan_id = Column(String, ForeignKey("iep_plans.id"), nullable=False)
    goal_code = Column(String, nullable=False)
    description = Column(String, nullable=False)
    target_date = Column(Date)
    status = Column(Enum(GoalStatusEnum), default=GoalStatusEnum.NOT_STARTED)
    sort_order = Column(Integer, default=0)
    
    plan = relationship("IepPlan", back_populates="goals")

class ProgressRecord(Base):
    __tablename__ = "progress_records"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_participant_id = Column(String, ForeignKey("session_participants.id"), nullable=False)
    iep_goal_id = Column(String, ForeignKey("iep_goals.id"), nullable=False)
    performance_score = Column(Float) # 0-100
    observations = Column(String)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
