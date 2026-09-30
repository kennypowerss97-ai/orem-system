from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time, datetime
from app.models.session import SessionTypeEnum, SessionStatusEnum

class SessionParticipantBase(BaseModel):
    student_id: str
    attended: bool = False
    absence_reason: Optional[str] = None
    is_telafi_eligible: bool = False

class SessionParticipantResponse(SessionParticipantBase):
    id: str
    session_id: str
    class Config:
        from_attributes = True

class SessionBase(BaseModel):
    module_id: int
    therapist_id: str
    room_id: int
    session_date: date
    start_time: time
    end_time: time
    session_type: SessionTypeEnum = SessionTypeEnum.INDIVIDUAL
    status: SessionStatusEnum = SessionStatusEnum.SCHEDULED
    cancellation_reason: Optional[str] = None

class SessionCreate(SessionBase):
    participant_student_ids: List[str]

class SessionUpdate(BaseModel):
    status: Optional[SessionStatusEnum] = None
    cancellation_reason: Optional[str] = None

class SessionResponse(SessionBase):
    id: str
    participants: List[SessionParticipantResponse] = []
    class Config:
        from_attributes = True

class AttendanceCreate(BaseModel):
    attended: bool
    absence_reason: Optional[str] = None

class TherapyModuleCreate(BaseModel):
    code: str
    title: str
    default_duration_minutes: int = 45
    is_group_eligible: bool = False

class TherapyModuleResponse(TherapyModuleCreate):
    id: int
    class Config:
        from_attributes = True

class RoomCreate(BaseModel):
    name: str
    code: str
    max_capacity: int = 1
    is_active: bool = True
    module_ids: List[int] = []

class RoomResponse(BaseModel):
    id: int
    name: str
    code: str
    max_capacity: int
    is_active: bool
    class Config:
        from_attributes = True
