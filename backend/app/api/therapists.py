from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import time

from app.database import get_db
from app.models.therapist import Therapist, TherapistSpecialization, TherapistAvailability
from app.models.session import TherapySession

router = APIRouter()

@router.get("")
@router.get("/")
async def list_therapists(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Therapist)
        .options(
            selectinload(Therapist.specializations),
            selectinload(Therapist.availability)
        )
    )
    therapists = result.scalars().all()

    data = []
    for t in therapists:
        specs = [{"moduleId": str(s.module_id)} for s in t.specializations]
        avails = [
            {
                "dayOfWeek": a.day_of_week,
                "startTime": a.start_time.strftime("%H:%M"),
                "endTime": a.end_time.strftime("%H:%M")
            }
            for a in t.availability
        ]

        data.append({
            "id": t.id,
            "firstName": t.first_name,
            "lastName": t.last_name,
            "title": t.title,
            "phone": t.phone,
            "email": t.email,
            "weeklyHours": t.max_weekly_hours,
            "currentWorkload": 24, # hours
            "specializations": specs,
            "availabilities": avails,
            "status": "active" if t.is_active else "inactive"
        })

    return {"data": data, "total": len(data), "page": 1, "limit": 100}

@router.post("")
@router.post("/")
async def create_therapist(data: dict, db: AsyncSession = Depends(get_db)):
    tc = data.get("tcKimlik") or data.get("identityNumber") or data.get("tc_kimlik")
    if not tc:
        import uuid
        tc = str(uuid.uuid4().int)[:11]

    # Duplicate TC kontrolü
    existing = await db.execute(select(Therapist).filter(Therapist.tc_kimlik == tc))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Bu TC Kimlik ({tc}) ile kayıtlı bir öğretmen zaten var.")

    try:
        t = Therapist(
            tc_kimlik=tc,
            first_name=data.get("firstName") or data.get("first_name", ""),
            last_name=data.get("lastName") or data.get("last_name", ""),
            title=data.get("title", "Terapist"),
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            max_weekly_hours=int(data.get("weeklyHours", 40)),
            is_active=True
        )
        db.add(t)
        await db.flush()

        # Specializations
        specs = data.get("specializations", [])
        for sp in specs:
            mod_id = sp.get("moduleId") if isinstance(sp, dict) else sp
            spec_obj = TherapistSpecialization(therapist_id=t.id, module_id=int(mod_id))
            db.add(spec_obj)

        # Availabilities
        avails = data.get("availabilities", [])
        if not avails:
            # Default Mon-Fri 09-17
            for d in range(1, 6):
                av = TherapistAvailability(
                    therapist_id=t.id,
                    day_of_week=d,
                    start_time=time(9, 0),
                    end_time=time(17, 0)
                )
                db.add(av)
        else:
            for a in avails:
                st_parts = [int(x) for x in a.get("startTime", "09:00").split(":")]
                et_parts = [int(x) for x in a.get("endTime", "17:00").split(":")]
                av = TherapistAvailability(
                    therapist_id=t.id,
                    day_of_week=int(a.get("dayOfWeek", 1)),
                    start_time=time(st_parts[0], st_parts[1]),
                    end_time=time(et_parts[0], et_parts[1])
                )
                db.add(av)

        await db.commit()
        return {"id": t.id, "message": "Öğretmen/Terapist kaydedildi."}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Bu bilgilerle kayıtlı bir öğretmen zaten mevcut.")

@router.get("/{id}")
async def get_therapist(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Therapist)
        .filter(Therapist.id == id)
        .options(
            selectinload(Therapist.specializations),
            selectinload(Therapist.availability)
        )
    )
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Terapist bulunamadı.")

    specs = [{"moduleId": str(s.module_id)} for s in t.specializations]
    avails = [
        {
            "dayOfWeek": a.day_of_week,
            "startTime": a.start_time.strftime("%H:%M"),
            "endTime": a.end_time.strftime("%H:%M")
        }
        for a in t.availability
    ]

    return {
        "id": t.id,
        "firstName": t.first_name,
        "lastName": t.last_name,
        "title": t.title,
        "phone": t.phone,
        "email": t.email,
        "weeklyHours": t.max_weekly_hours,
        "currentWorkload": 20,
        "specializations": specs,
        "availabilities": avails
    }

@router.put("/{id}")
async def update_therapist(id: str, data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Therapist)
        .filter(Therapist.id == id)
        .options(
            selectinload(Therapist.specializations),
            selectinload(Therapist.availability)
        )
    )
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Terapist bulunamadı")
    
    if "firstName" in data:
        t.first_name = data["firstName"]
    if "lastName" in data:
        t.last_name = data["lastName"]
    if "tcKimlik" in data:
        t.tc_kimlik = data["tcKimlik"]
    if "title" in data:
        t.title = data["title"]
    if "phone" in data:
        t.phone = data["phone"]
    if "email" in data:
        t.email = data["email"]
    if "weeklyHours" in data:
        t.max_weekly_hours = int(data["weeklyHours"])
    if "is_active" in data:
        t.is_active = data["is_active"]

    if "specializations" in data and isinstance(data["specializations"], list):
        for s in list(t.specializations):
            await db.delete(s)
        for sp in data["specializations"]:
            mod_id = sp.get("moduleId") if isinstance(sp, dict) else sp
            spec_obj = TherapistSpecialization(therapist_id=t.id, module_id=int(mod_id))
            db.add(spec_obj)

    if "availabilities" in data and isinstance(data["availabilities"], list):
        for a in list(t.availability):
            await db.delete(a)
        for a in data["availabilities"]:
            st_parts = [int(x) for x in a.get("startTime", "09:00").split(":")]
            et_parts = [int(x) for x in a.get("endTime", "17:00").split(":")]
            av = TherapistAvailability(
                therapist_id=t.id,
                day_of_week=int(a.get("dayOfWeek", 1)),
                start_time=time(st_parts[0], st_parts[1]),
                end_time=time(et_parts[0], et_parts[1])
            )
            db.add(av)
    
    await db.commit()
    return {"id": t.id, "message": "Öğretmen başarıyla güncellendi."}

@router.delete("/{id}")
async def delete_therapist(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Therapist).filter(Therapist.id == id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Terapist bulunamadı")
    t.is_active = False
    await db.commit()
    return {"message": "Öğretmen silindi."}


@router.get("/{id}/schedule")
async def get_therapist_schedule(id: str, db: AsyncSession = Depends(get_db)):
    query = await db.execute(
        select(TherapySession)
        .filter(TherapySession.therapist_id == id)
        .order_by(TherapySession.session_date, TherapySession.start_time)
    )
    sessions = query.scalars().all()
    return [
        {
            "id": sess.id,
            "date": str(sess.session_date),
            "startTime": sess.start_time.strftime("%H:%M"),
            "endTime": sess.end_time.strftime("%H:%M"),
            "moduleId": sess.module_id,
            "roomId": sess.room_id,
            "status": sess.status.value.lower()
        }
        for sess in sessions
    ]

@router.get("/{id}/workload")
async def get_therapist_workload(id: str, db: AsyncSession = Depends(get_db)):
    return {
        "totalAssignedHours": 24,
        "maxWeeklyHours": 40,
        "utilizationRate": 60
    }
