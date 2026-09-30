from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time

class ScheduleSlot(BaseModel):
    session_id: Optional[str] = None
    date: date
    start_time: time
    end_time: time
    therapist_id: str
    room_id: int
    student_ids: List[str]

class ScheduleGenerateRequest(BaseModel):
    start_date: date
    end_date: date

class ScheduleGenerateResponse(BaseModel):
    status: str
    sessions_created: int
    message: str

class WeeklyScheduleResponse(BaseModel):
    slots: List[ScheduleSlot]
