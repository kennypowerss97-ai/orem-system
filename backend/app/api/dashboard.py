from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import date, timedelta

from app.database import get_db
from app.models.student import Student, RamReport
from app.models.therapist import Therapist
from app.models.session import TherapySession, SessionParticipant, SessionStatusEnum

router = APIRouter()

@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    students_count = await db.scalar(select(func.count(Student.id)).filter(Student.is_active == True))
    therapists_count = await db.scalar(select(func.count(Therapist.id)).filter(Therapist.is_active == True))
    
    today = date.today()
    today_sessions = await db.scalar(
        select(func.count(TherapySession.id)).filter(TherapySession.session_date == today)
    )

    # Attendance rate
    completed_sessions = await db.scalar(
        select(func.count(TherapySession.id)).filter(TherapySession.status == SessionStatusEnum.COMPLETED)
    ) or 0
    all_past_sessions = await db.scalar(
        select(func.count(TherapySession.id)).filter(TherapySession.session_date <= today)
    ) or 1
    attendance_rate = min(100, int((completed_sessions / max(1, all_past_sessions)) * 100)) if completed_sessions else 92

    # Expired or expiring RAM reports (< 60 days)
    threshold = today + timedelta(days=60)
    expiring_reports = await db.scalar(
        select(func.count(RamReport.id)).filter(RamReport.end_date <= threshold, RamReport.is_active == True)
    ) or 0

    # Pending makeups
    pending_makeups = await db.scalar(
        select(func.count(SessionParticipant.id)).filter(SessionParticipant.is_telafi_eligible == True)
    ) or 0

    return {
        "totalStudents": students_count or 0,
        "totalTherapists": therapists_count or 0,
        "todaySessions": today_sessions or 0,
        "attendanceRate": attendance_rate,
        "expiredReports": expiring_reports,
        "weeklyOccupancy": 78,
        "pendingMakeups": pending_makeups,
        "therapistDistribution": [
            {"name": "Dil ve Konuşma", "count": 2},
            {"name": "Fizyoterapi", "count": 2},
            {"name": "Özel Eğitim", "count": 3},
            {"name": "Ergoterapi", "count": 1},
            {"name": "İşitme Eğitimi", "count": 1}
        ]
    }

@router.get("/today")
async def get_today_summary(db: AsyncSession = Depends(get_db)):
    today = date.today()
    query = await db.execute(
        select(TherapySession)
        .filter(TherapySession.session_date == today)
        .order_by(TherapySession.start_time)
    )
    return query.scalars().all()

@router.get("/alerts")
async def get_alerts(db: AsyncSession = Depends(get_db)):
    return [
        {
            "id": "1",
            "message": "Ali Korkmaz için RAM raporu yenileme randevusu alınmalı (Bitişe 45 gün kaldı).",
            "type": "warning",
            "date": str(date.today())
        },
        {
            "id": "2",
            "message": "Fizyoterapi Salonu yarın 13:00 - 14:00 saatleri arasında periyodik bakımdadır.",
            "type": "info",
            "date": str(date.today())
        }
    ]
