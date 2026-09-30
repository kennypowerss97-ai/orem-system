from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from app.models.iep import GoalStatusEnum

class ProgressRecordBase(BaseModel):
    session_participant_id: str
    iep_goal_id: str
    performance_score: Optional[float] = None
    observations: Optional[str] = None

class ProgressRecordCreate(ProgressRecordBase):
    pass

class ProgressRecordResponse(ProgressRecordBase):
    id: str
    recorded_at: datetime
    class Config:
        from_attributes = True

class IepGoalBase(BaseModel):
    goal_code: str
    description: str
    target_date: Optional[date] = None
    status: GoalStatusEnum = GoalStatusEnum.NOT_STARTED
    sort_order: int = 0

class IepGoalCreate(IepGoalBase):
    pass

class IepGoalResponse(IepGoalBase):
    id: str
    iep_plan_id: str
    class Config:
        from_attributes = True

class IepPlanBase(BaseModel):
    student_id: str
    module_id: int
    coordinator_therapist_id: str
    start_date: date
    end_date: date
    notes: Optional[str] = None

class IepPlanCreate(IepPlanBase):
    goals: List[IepGoalCreate] = []

class IepPlanResponse(IepPlanBase):
    id: str
    goals: List[IepGoalResponse] = []
    class Config:
        from_attributes = True
