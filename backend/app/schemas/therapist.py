from pydantic import BaseModel
from typing import Optional, List
from datetime import time

class SpecializationCreate(BaseModel):
    module_id: int
    is_primary: bool = True

class AvailabilityBase(BaseModel):
    day_of_week: int
    start_time: time
    end_time: time

class AvailabilityCreate(AvailabilityBase):
    pass

class AvailabilityResponse(AvailabilityBase):
    id: int
    therapist_id: str
    class Config:
        from_attributes = True

class TherapistBase(BaseModel):
    tc_kimlik: Optional[str] = None
    first_name: str
    last_name: str
    title: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    max_weekly_hours: int = 40
    is_active: bool = True

class TherapistCreate(TherapistBase):
    specializations: List[SpecializationCreate] = []
    availability: List[AvailabilityCreate] = []

class TherapistUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None

class TherapistResponse(TherapistBase):
    id: str
    availability: List[AvailabilityResponse] = []
    class Config:
        from_attributes = True

class TherapistListResponse(BaseModel):
    total: int
    items: List[TherapistResponse]
