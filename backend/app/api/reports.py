from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

@router.get("/progress/{student_id}")
async def get_student_progress_report(student_id: str, db: AsyncSession = Depends(get_db)):
    return {
        "studentId": student_id,
        "overallScore": 84,
        "milestonesAchieved": 14,
        "milestonesTotal": 18,
        "monthlyData": [
            {"month": "Mayıs", "skor": 65},
            {"month": "Haziran", "skor": 70},
            {"month": "Temmuz", "skor": 78},
            {"month": "Ağustos", "skor": 82},
            {"month": "Eylül", "skor": 88}
        ]
    }

@router.get("/attendance/monthly")
async def get_monthly_attendance_report(db: AsyncSession = Depends(get_db)):
    return {
        "attendanceRate": 94,
        "totalConducted": 284,
        "totalAbsent": 18,
        "totalMakeups": 14
    }

@router.get("/therapist-workload")
async def get_therapists_workload_report(db: AsyncSession = Depends(get_db)):
    return [
        {"therapist": "Ayşe Yılmaz", "hours": 32, "max": 40},
        {"therapist": "Mehmet Demir", "hours": 36, "max": 40},
        {"therapist": "Fatma Kaya", "hours": 28, "max": 40},
        {"therapist": "Can Şahin", "hours": 30, "max": 40},
        {"therapist": "Zeynep Aydın", "hours": 24, "max": 40}
    ]

@router.get("/capacity")
async def get_center_capacity_report(db: AsyncSession = Depends(get_db)):
    return {
        "overallUtilization": 76,
        "rooms": [
            {"room": "Dil ve Konuşma Odası 1", "rate": 85},
            {"room": "Fizyoterapi Salonu", "rate": 90},
            {"room": "Bireysel Eğitim 1", "rate": 70},
            {"room": "Bireysel Eğitim 2", "rate": 65},
            {"room": "Duyu Bütünleme Odası", "rate": 80}
        ]
    }
