from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import date, timedelta

from app.database import get_db
from app.services.scheduler_engine import SchedulerEngine
from app.models.session import TherapySession, SessionParticipant
from app.models.student import Student
from app.models.therapist import Therapist
from app.models.room import Room
from app.models.therapy_module import TherapyModule

router = APIRouter()

MODULE_COLORS = {
    1: "#1890ff", # Dil (Mavi)
    2: "#52c41a", # Fizyo (Yeşil)
    3: "#fa8c16", # Özel Öğrenme (Turuncu)
    4: "#722ed1", # Otizm (Mor)
    5: "#eb2f96", # Zihinsel (Pembe)
    6: "#13c2c2", # İşitme
    7: "#faad14", # Görme
}

@router.post("/generate")
async def generate_schedule(data: dict = {}, db: AsyncSession = Depends(get_db)):
    start_str = data.get("startDate")
    end_str = data.get("endDate")
    start_d = date.fromisoformat(start_str) if start_str else None
    end_d = date.fromisoformat(end_str) if end_str else None

    engine = SchedulerEngine()
    result = await engine.generate_full_schedule(db, start_date=start_d, end_date=end_d)
    return result

@router.post("/student/{student_id}")
async def add_student_schedule(student_id: str, data: dict = {}, db: AsyncSession = Depends(get_db)):
    engine = SchedulerEngine()
    result = await engine.add_student_to_existing_schedule(db, student_id=student_id)
    return result

@router.get("/weekly")
async def get_weekly_schedule(
    week_start: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    therapist_id: Optional[str] = None,
    room_id: Optional[int] = None,
    student_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    # Parse start date
    raw_start = start_date or start or week_start
    if raw_start:
        start_d = date.fromisoformat(str(raw_start).split("T")[0])
    else:
        # Default to 30 days past and 90 days future so future & current sessions always load
        start_d = date.today() - timedelta(days=30)

    # Parse end date
    raw_end = end_date or end
    if raw_end:
        end_d = date.fromisoformat(str(raw_end).split("T")[0])
    elif raw_start and week_start:
        end_d = start_d + timedelta(days=6)
    else:
        end_d = date.today() + timedelta(days=90)

    query = select(TherapySession).filter(
        TherapySession.session_date >= start_d,
        TherapySession.session_date <= end_d
    ).options(selectinload(TherapySession.participants))

    if therapist_id:
        query = query.filter(TherapySession.therapist_id == therapist_id)
    if room_id:
        query = query.filter(TherapySession.room_id == room_id)

    result = await db.execute(query)
    sessions = result.scalars().all()

    students_map = {s.id: f"{s.first_name} {s.last_name}" for s in (await db.execute(select(Student))).scalars().all()}
    therapists_map = {t.id: f"{t.first_name} {t.last_name}" for t in (await db.execute(select(Therapist))).scalars().all()}
    rooms_map = {r.id: r.name for r in (await db.execute(select(Room))).scalars().all()}
    modules_map = {m.id: m.title for m in (await db.execute(select(TherapyModule))).scalars().all()}

    events = []
    for sess in sessions:
        p_names = [students_map.get(p.student_id, "Öğrenci") for p in sess.participants]
        if student_id and not any(p.student_id == student_id for p in sess.participants):
            continue

        st_title = ", ".join(p_names) if p_names else "Boş Seans"
        t_name = therapists_map.get(sess.therapist_id, "Terapist")
        r_name = rooms_map.get(sess.room_id, "Oda")
        m_title = modules_map.get(sess.module_id, "Eğitim")

        first_student_id = sess.participants[0].student_id if sess.participants else None

        events.append({
            "id": sess.id,
            "title": f"{st_title} - {m_title} ({t_name})",
            "start": f"{sess.session_date}T{sess.start_time.strftime('%H:%M:%S')}",
            "end": f"{sess.session_date}T{sess.end_time.strftime('%H:%M:%S')}",
            "backgroundColor": MODULE_COLORS.get(sess.module_id, "#1890ff"),
            "borderColor": MODULE_COLORS.get(sess.module_id, "#1890ff"),
            "extendedProps": {
                "sessionId": sess.id,
                "studentId": first_student_id,
                "therapistId": sess.therapist_id,
                "roomId": sess.room_id,
                "moduleId": sess.module_id,
                "date": str(sess.session_date),
                "startTime": sess.start_time.strftime("%H:%M"),
                "endTime": sess.end_time.strftime("%H:%M"),
                "studentName": st_title,
                "therapistName": t_name,
                "roomName": r_name,
                "moduleName": m_title,
                "status": sess.status.value.lower()
            }
        })

    return events

@router.put("/sessions/{session_id}/move")
async def move_session(session_id: str, data: dict, db: AsyncSession = Depends(get_db)):
    from datetime import datetime
    query = await db.execute(
        select(TherapySession)
        .filter(TherapySession.id == session_id)
    )
    sess = query.scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Seans bulunamadı")

    if "start" in data:
        dt = datetime.fromisoformat(data["start"].replace("Z", "").split("+")[0])
        sess.session_date = dt.date()
        sess.start_time = dt.time()
    if "end" in data:
        dt = datetime.fromisoformat(data["end"].replace("Z", "").split("+")[0])
        sess.end_time = dt.time()
    await db.commit()
    return {"message": "Seans başarıyla taşındı"}

@router.get("/conflicts")
async def get_conflicts(db: AsyncSession = Depends(get_db)):
    return []

