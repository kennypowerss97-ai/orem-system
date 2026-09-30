from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import date, time

from app.database import get_db
from app.models.session import TherapySession, SessionParticipant, SessionStatusEnum
from app.models.student import Student
from app.models.therapist import Therapist
from app.models.therapy_module import TherapyModule
from app.models.room import Room

router = APIRouter()

@router.get("/")
async def get_sessions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    therapist_id: Optional[str] = None,
    room_id: Optional[int] = None,
    student_id: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(TherapySession).options(
        selectinload(TherapySession.participants)
    ).order_by(TherapySession.session_date, TherapySession.start_time)

    if start_date:
        query = query.filter(TherapySession.session_date >= date.fromisoformat(start_date))
    if end_date:
        query = query.filter(TherapySession.session_date <= date.fromisoformat(end_date))
    if therapist_id:
        query = query.filter(TherapySession.therapist_id == therapist_id)
    if room_id:
        query = query.filter(TherapySession.room_id == room_id)

    result = await db.execute(query)
    sessions = result.scalars().all()

    # Preload names
    students_map = {s.id: f"{s.first_name} {s.last_name}" for s in (await db.execute(select(Student))).scalars().all()}
    therapists_map = {t.id: f"{t.first_name} {t.last_name}" for t in (await db.execute(select(Therapist))).scalars().all()}
    modules_map = {m.id: m.title for m in (await db.execute(select(TherapyModule))).scalars().all()}
    rooms_map = {r.id: r.name for r in (await db.execute(select(Room))).scalars().all()}

    data = []
    for sess in sessions:
        participants = [
            {
                "studentId": p.student_id,
                "studentName": students_map.get(p.student_id, "Öğrenci"),
                "attendanceStatus": "present" if p.attended else "planned",
                "isTelafiEligible": p.is_telafi_eligible
            }
            for p in sess.participants
        ]

        if student_id and not any(p["studentId"] == student_id for p in participants):
            continue

        data.append({
            "id": sess.id,
            "moduleId": str(sess.module_id),
            "moduleName": modules_map.get(sess.module_id, "Modül"),
            "therapistId": sess.therapist_id,
            "therapistName": therapists_map.get(sess.therapist_id, "Terapist"),
            "roomId": str(sess.room_id),
            "roomName": rooms_map.get(sess.room_id, "Oda"),
            "date": str(sess.session_date),
            "startTime": sess.start_time.strftime("%H:%M"),
            "endTime": sess.end_time.strftime("%H:%M"),
            "status": sess.status.value.lower(),
            "participants": participants
        })

    return {"data": data, "total": len(data), "page": 1, "limit": 200}

@router.get("/today")
async def get_today_sessions(db: AsyncSession = Depends(get_db)):
    res = await get_sessions(start_date=str(date.today()), end_date=str(date.today()), db=db)
    return res.get("data", [])

@router.post("")
@router.post("/")
async def create_session(data: dict, db: AsyncSession = Depends(get_db)):
    st_raw = data.get("startTime", "09:00")
    et_raw = data.get("endTime", "09:45")
    st_parts = [int(x) for x in st_raw.split(":")]
    et_parts = [int(x) for x in et_raw.split(":")]
    
    date_raw = data.get("date")
    sess_date = date.fromisoformat(str(date_raw).split("T")[0]) if date_raw else date.today()

    session = TherapySession(
        module_id=int(data.get("moduleId", 1)),
        therapist_id=str(data.get("therapistId")),
        room_id=int(data.get("roomId", 1)),
        session_date=sess_date,
        start_time=time(st_parts[0], st_parts[1]),
        end_time=time(et_parts[0], et_parts[1]),
        status=SessionStatusEnum.SCHEDULED
    )
    db.add(session)
    await db.flush()

    # Participant student
    student_id = data.get("studentId")
    if student_id:
        participant = SessionParticipant(
            session_id=session.id,
            student_id=str(student_id),
            attended=False
        )
        db.add(participant)
    elif data.get("participant_student_ids"):
        for sid in data["participant_student_ids"]:
            db.add(SessionParticipant(session_id=session.id, student_id=str(sid), attended=False))

    await db.commit()
    return {"message": "Ders/Seans başarıyla oluşturuldu.", "id": session.id}


@router.get("/{id}")
async def get_session(id: str, db: AsyncSession = Depends(get_db)):
    query = await db.execute(
        select(TherapySession)
        .filter(TherapySession.id == id)
        .options(selectinload(TherapySession.participants))
    )
    sess = query.scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Seans bulunamadı")
    return {
        "id": sess.id,
        "moduleId": str(sess.module_id),
        "therapistId": sess.therapist_id,
        "roomId": str(sess.room_id),
        "date": str(sess.session_date),
        "startTime": sess.start_time.strftime("%H:%M"),
        "endTime": sess.end_time.strftime("%H:%M"),
        "status": sess.status.value.lower(),
        "participants": [{"studentId": p.student_id, "attendanceStatus": "present" if p.attended else "planned"} for p in sess.participants]
    }

@router.post("/{id}/attendance")
async def mark_attendance(id: str, data: dict, db: AsyncSession = Depends(get_db)):
    query = await db.execute(
        select(TherapySession)
        .filter(TherapySession.id == id)
        .options(selectinload(TherapySession.participants))
    )
    sess = query.scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Seans bulunamadı")

    attended = data.get("attended", True)
    sess.status = SessionStatusEnum.COMPLETED if attended else SessionStatusEnum.STUDENT_ABSENT
    for p in sess.participants:
        p.attended = attended
        if not attended:
            p.absence_reason = data.get("absence_reason", "Mazeretli")
            p.is_telafi_eligible = True

    await db.commit()
    return {"message": "Yoklama kaydedildi.", "status": sess.status.value.lower()}

@router.post("/{id}/cancel")
async def cancel_session(id: str, data: dict, db: AsyncSession = Depends(get_db)):
    query = await db.execute(
        select(TherapySession)
        .filter(TherapySession.id == id)
        .options(selectinload(TherapySession.participants))
    )
    sess = query.scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Seans bulunamadı")

    sess.status = SessionStatusEnum.CANCELLED
    sess.cancellation_reason = data.get("reason", "İptal edildi")
    for p in sess.participants:
        p.is_telafi_eligible = True

    await db.commit()
    return {"message": "Seans iptal edildi ve öğrencilere telafi hakkı tanımlandı."}

@router.put("/{id}")
async def update_session(id: str, data: dict, db: AsyncSession = Depends(get_db)):
    query = await db.execute(
        select(TherapySession)
        .filter(TherapySession.id == id)
        .options(selectinload(TherapySession.participants))
    )
    sess = query.scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Seans bulunamadı")

    if "date" in data and data["date"]:
        sess.session_date = date.fromisoformat(str(data["date"]).split("T")[0])
    if "startTime" in data and data["startTime"]:
        st_parts = [int(x) for x in data["startTime"].split(":")]
        sess.start_time = time(st_parts[0], st_parts[1])
    if "endTime" in data and data["endTime"]:
        et_parts = [int(x) for x in data["endTime"].split(":")]
        sess.end_time = time(et_parts[0], et_parts[1])
    if "therapistId" in data and data["therapistId"]:
        sess.therapist_id = data["therapistId"]
    if "roomId" in data and data["roomId"]:
        sess.room_id = int(data["roomId"])
    if "moduleId" in data and data["moduleId"]:
        sess.module_id = int(data["moduleId"])
    if "status" in data and data["status"]:
        status_str = data["status"].upper()
        if status_str in SessionStatusEnum.__members__:
            sess.status = SessionStatusEnum[status_str]

    if "studentId" in data and data["studentId"]:
        # Update or add participant
        if sess.participants:
            sess.participants[0].student_id = data["studentId"]
        else:
            db.add(SessionParticipant(session_id=sess.id, student_id=data["studentId"]))

    await db.commit()
    return {"message": "Seans başarıyla güncellendi", "id": sess.id}

@router.delete("/{id}")
async def delete_session(id: str, db: AsyncSession = Depends(get_db)):
    query = await db.execute(
        select(TherapySession)
        .filter(TherapySession.id == id)
        .options(selectinload(TherapySession.participants))
    )
    sess = query.scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Seans bulunamadı")

    for p in sess.participants:
        await db.delete(p)
    await db.delete(sess)
    await db.commit()
    return {"message": "Seans başarıyla silindi"}

