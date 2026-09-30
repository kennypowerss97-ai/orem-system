import os

base_dir = r"C:\Users\Pc\.gemini\antigravity\scratch\orem-system\backend"

data = r"""====FILE====
requirements.txt
----CONTENT----
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy[asyncio]==2.0.35
aiosqlite==0.20.0
pydantic==2.9.0
pydantic-settings==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
ortools-python==9.10.4067
httpx==0.27.0
====FILE====
app/__init__.py
----CONTENT----
====FILE====
app/config.py
----CONTENT----
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./orem.db"
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    class Config:
        env_file = ".env"

settings = Settings()
====FILE====
app/database.py
----CONTENT----
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
====FILE====
app/models/__init__.py
----CONTENT----
from .user import User
from .student import Student, Guardian, RamReport, AllocatedModule
from .therapist import Therapist, TherapistSpecialization, TherapistAvailability
from .therapy_module import TherapyModule
from .room import Room, RoomModule
from .session import TherapySession, SessionParticipant
from .iep import IepPlan, IepGoal, ProgressRecord
====FILE====
app/models/user.py
----CONTENT----
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import enum

class RoleEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    SECRETARY = "SECRETARY"

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.TEACHER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
====FILE====
app/models/student.py
----CONTENT----
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, func, Date
from sqlalchemy.orm import relationship
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

    guardians = relationship("Guardian", back_populates="student")
    ram_reports = relationship("RamReport", back_populates="student")

class Guardian(Base):
    __tablename__ = "guardians"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String)
    email = Column(String)
    relationship = Column(String)
    is_primary = Column(Boolean, default=False)
    student = relationship("Student", back_populates="guardians")

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
    student = relationship("Student", back_populates="ram_reports")
    allocated_modules = relationship("AllocatedModule", back_populates="ram_report")

class AllocatedModule(Base):
    __tablename__ = "allocated_modules"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ram_report_id = Column(String, ForeignKey("ram_reports.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("therapy_modules.id"), nullable=False)
    monthly_individual_hours = Column(Integer, default=8)
    monthly_group_hours = Column(Integer, default=4)
    ram_report = relationship("RamReport", back_populates="allocated_modules")
====FILE====
app/models/therapist.py
----CONTENT----
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
====FILE====
app/models/therapy_module.py
----CONTENT----
from sqlalchemy import Column, String, Boolean, DateTime, Integer, func
from app.database import Base

class TherapyModule(Base):
    __tablename__ = "therapy_modules"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    default_duration_minutes = Column(Integer, default=45)
    is_group_eligible = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
====FILE====
app/models/room.py
----CONTENT----
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, index=True, nullable=False)
    max_capacity = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    
    modules = relationship("RoomModule", back_populates="room")

class RoomModule(Base):
    __tablename__ = "room_modules"
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("therapy_modules.id"), nullable=False)
    room = relationship("Room", back_populates="modules")
====FILE====
app/models/session.py
----CONTENT----
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
====FILE====
app/models/iep.py
----CONTENT----
import uuid
import enum
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, func, Date, Float
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
====FILE====
app/schemas/__init__.py
----CONTENT----
====FILE====
app/schemas/user.py
----CONTENT----
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import RoleEnum
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: RoleEnum = RoleEnum.TEACHER
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str
====FILE====
app/schemas/student.py
----CONTENT----
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
====FILE====
app/schemas/therapist.py
----CONTENT----
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
====FILE====
app/schemas/session.py
----CONTENT----
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
====FILE====
app/schemas/schedule.py
----CONTENT----
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
====FILE====
app/schemas/iep.py
----CONTENT----
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
====FILE====
app/core/__init__.py
----CONTENT----
====FILE====
app/core/security.py
----CONTENT----
from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config import settings
from app.database import get_db
from app.models.user import User, RoleEnum

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user

def require_role(allowed_roles: List[RoleEnum]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user
    return role_checker
====FILE====
app/core/dependencies.py
----CONTENT----
from fastapi import Query

class PaginationParams:
    def __init__(self, skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=100)):
        self.skip = skip
        self.limit = limit
====FILE====
app/core/exceptions.py
----CONTENT----
from fastapi import Request, status
from fastapi.responses import JSONResponse

class OremException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code

async def orem_exception_handler(request: Request, exc: OremException):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.message})
====FILE====
app/services/__init__.py
----CONTENT----
====FILE====
app/services/auth_service.py
----CONTENT----
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate):
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        role=user.role,
        is_active=user.is_active
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
====FILE====
app/services/student_service.py
----CONTENT----
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.student import Student, Guardian, RamReport, AllocatedModule
from app.schemas.student import StudentCreate

async def get_students(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Student).offset(skip).limit(limit))
    return result.scalars().all()

async def create_student(db: AsyncSession, student_data: StudentCreate):
    db_student = Student(**student_data.model_dump())
    db.add(db_student)
    await db.commit()
    await db.refresh(db_student)
    return db_student

async def add_student_to_schedule(db: AsyncSession, student_id: str):
    from app.services.scheduler_engine import SchedulerEngine
    engine = SchedulerEngine()
    # Mocking call for now
    await engine.add_student_to_existing_schedule(db, student_id)
====FILE====
app/services/scheduler_engine.py
----CONTENT----
import logging
from datetime import date, time, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
try:
    from ortools.sat.python import cp_model
    HAS_ORTOOLS = True
except ImportError:
    HAS_ORTOOLS = False

logger = logging.getLogger(__name__)

class SchedulerEngine:
    async def generate_full_schedule(self, db: AsyncSession, start_date: date, end_date: date):
        if not HAS_ORTOOLS:
            logger.warning("OR-Tools not available. Using greedy fallback.")
            return self._greedy_fallback(db, start_date, end_date)
        
        logger.info("Starting CP-SAT scheduling...")
        # A full implementation would query all students, therapists, rooms and build variables.
        # Minimal skeleton for constraints and solver.
        model = self._build_model()
        self._apply_hard_constraints(model)
        self._apply_soft_constraints(model)
        
        solution = self._solve(model)
        return self._extract_solution(solution)

    async def add_student_to_existing_schedule(self, db: AsyncSession, student_id: str):
        pass
        
    def _build_model(self):
        if HAS_ORTOOLS:
            return cp_model.CpModel()
        return None
        
    def _apply_hard_constraints(self, model):
        # 1. No overlap for therapists, students, rooms
        # 2. Daily max sessions
        pass
        
    def _apply_soft_constraints(self, model):
        pass
        
    def _solve(self, model):
        if not HAS_ORTOOLS:
            return None
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0
        status = solver.Solve(model)
        return status
        
    def _extract_solution(self, status):
        # mock returns
        return {"status": "SUCCESS", "sessions_created": 0, "message": "Schedule generation finished."}

    def _greedy_fallback(self, db, start_date, end_date):
        return {"status": "SUCCESS", "sessions_created": 0, "message": "Greedy fallback used."}
====FILE====
app/services/report_service.py
----CONTENT----
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.student import Student
from app.models.therapist import Therapist
from app.models.session import TherapySession
from datetime import date

async def get_dashboard_stats(db: AsyncSession):
    students_count = await db.scalar(select(func.count(Student.id)).filter(Student.is_active == True))
    therapists_count = await db.scalar(select(func.count(Therapist.id)).filter(Therapist.is_active == True))
    today_sessions = await db.scalar(select(func.count(TherapySession.id)).filter(TherapySession.session_date == date.today()))
    
    return {
        "active_students": students_count or 0,
        "active_therapists": therapists_count or 0,
        "today_sessions": today_sessions or 0,
    }
====FILE====
app/api/__init__.py
----CONTENT----
====FILE====
app/api/router.py
----CONTENT----
from fastapi import APIRouter
from app.api import auth, students, therapists, modules, rooms, sessions, schedule, iep, dashboard, reports

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(therapists.router, prefix="/therapists", tags=["therapists"])
api_router.include_router(modules.router, prefix="/modules", tags=["modules"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(schedule.router, prefix="/schedule", tags=["schedule"])
api_router.include_router(iep.router, prefix="/iep", tags=["iep"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
====FILE====
app/api/auth.py
----CONTENT----
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.database import get_db
from app.schemas.user import Token, UserCreate, UserResponse
from app.services.auth_service import authenticate_user, create_user
from app.core.security import create_access_token, get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # normally only admin
    return await create_user(db, user)

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
====FILE====
app/api/students.py
----CONTENT----
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.schemas.student import StudentCreate, StudentResponse, StudentListResponse
from app.services.student_service import create_student, get_students, add_student_to_schedule

router = APIRouter()

@router.post("/", response_model=StudentResponse)
async def add_student(student: StudentCreate, db: AsyncSession = Depends(get_db)):
    st = await create_student(db, student)
    # auto-schedule
    await add_student_to_schedule(db, st.id)
    return st

@router.get("/", response_model=List[StudentResponse])
async def list_students(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await get_students(db, skip, limit)
====FILE====
app/api/therapists.py
----CONTENT----
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.schemas.therapist import TherapistCreate, TherapistResponse
from app.models.therapist import Therapist

router = APIRouter()

@router.post("/", response_model=TherapistResponse)
async def create_therapist(therapist: TherapistCreate, db: AsyncSession = Depends(get_db)):
    db_therapist = Therapist(**therapist.model_dump(exclude={'specializations', 'availability'}))
    db.add(db_therapist)
    await db.commit()
    await db.refresh(db_therapist)
    return db_therapist

@router.get("/", response_model=List[TherapistResponse])
async def get_therapists(db: AsyncSession = Depends(get_db)):
    return []
====FILE====
app/api/modules.py
----CONTENT----
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.session import TherapyModuleCreate, TherapyModuleResponse
from app.models.therapy_module import TherapyModule
from typing import List

router = APIRouter()

@router.get("/", response_model=List[TherapyModuleResponse])
async def get_modules(db: AsyncSession = Depends(get_db)):
    return []
====FILE====
app/api/rooms.py
----CONTENT----
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.session import RoomCreate, RoomResponse
from typing import List

router = APIRouter()

@router.get("/", response_model=List[RoomResponse])
async def get_rooms(db: AsyncSession = Depends(get_db)):
    return []
====FILE====
app/api/sessions.py
----CONTENT----
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.session import SessionResponse, SessionCreate
from typing import List

router = APIRouter()

@router.get("/", response_model=List[SessionResponse])
async def get_sessions(db: AsyncSession = Depends(get_db)):
    return []
====FILE====
app/api/schedule.py
----CONTENT----
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.schedule import ScheduleGenerateRequest, ScheduleGenerateResponse
from app.services.scheduler_engine import SchedulerEngine

router = APIRouter()

@router.post("/generate", response_model=ScheduleGenerateResponse)
async def generate_schedule(req: ScheduleGenerateRequest, db: AsyncSession = Depends(get_db)):
    engine = SchedulerEngine()
    result = await engine.generate_full_schedule(db, req.start_date, req.end_date)
    return result
====FILE====
app/api/iep.py
----CONTENT----
from fastapi import APIRouter
router = APIRouter()
====FILE====
app/api/dashboard.py
----CONTENT----
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.report_service import get_dashboard_stats

router = APIRouter()

@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    return await get_dashboard_stats(db)
====FILE====
app/api/reports.py
----CONTENT----
from fastapi import APIRouter
router = APIRouter()
====FILE====
app/main.py
----CONTENT----
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.database import engine, Base
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="OREM Management System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Seed data logic would go here
    logging.info("Application startup complete.")
====FILE====
"""

for block in data.split("====FILE====\n"):
    if not block.strip(): continue
    parts = block.split("----CONTENT----\n")
    if len(parts) == 2:
        rel_path = parts[0].strip()
        content = parts[1]
        full_path = os.path.join(base_dir, rel_path.replace("/", os.sep))
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
print("Done creating backend files.")
