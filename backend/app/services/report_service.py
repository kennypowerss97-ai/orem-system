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
