from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class GuardianBase(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    relationship: Optional[str] = None
    is_primary: bool = False

class GuardianCreate(GuardianBase):
    pass

class GuardianResponse(GuardianBase):
    id: str
    student_id: str
    
    class Config:
        from_attributes = True

class AllocatedModuleBase(BaseModel):
    module_id: int
    monthly_individual_hours: int = 8
    monthly_group_hours: int = 4

class AllocatedModuleCreate(AllocatedModuleBase):
    pass

class AllocatedModuleResponse(AllocatedModuleBase):
    id: int
    ram_report_id: str
    
    class Config:
        from_attributes = True

class RamReportBase(BaseModel):
    report_number: str
    issuing_ram: Optional[str] = None
    start_date: date
    end_date: date
    is_active: bool = True

class RamReportCreate(RamReportBase):
    allocated_modules: List[AllocatedModuleCreate] = []

class RamReportResponse(RamReportBase):
    id: str
    student_id: str
    created_at: datetime
    allocated_modules: List[AllocatedModuleResponse] = []
    
    class Config:
        from_attributes = True

class StudentBase(BaseModel):
    tc_kimlik: str
    first_name: str
    last_name: str
    birth_date: date
    gender: Optional[str] = None
    disability_type: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = True

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None

class StudentResponse(StudentBase):
    id: str
    created_at: datetime
    guardians: List[GuardianResponse] = []
    ram_reports: List[RamReportResponse] = []
    
    class Config:
        from_attributes = True

class StudentListResponse(BaseModel):
    total: int
    items: List[StudentResponse]
