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
