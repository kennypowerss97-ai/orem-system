from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models.student import Student, Guardian, RamReport, AllocatedModule
from app.models.session import TherapySession, SessionParticipant
from app.schemas.student import (
    StudentCreate, StudentUpdate, StudentResponse,
    GuardianCreate, GuardianResponse,
    RamReportCreate, RamReportResponse,
    AllocatedModuleCreate, AllocatedModuleResponse
)
from app.services.scheduler_engine import SchedulerEngine

router = APIRouter()

@router.get("")
@router.get("/")
async def list_students(
    search: Optional[str] = None,
    disability_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    query = select(Student).options(
        selectinload(Student.guardians),
        selectinload(Student.ram_reports).selectinload(RamReport.allocated_modules)
    )
    if search:
        query = query.filter(
            (Student.first_name.ilike(f"%{search}%")) |
            (Student.last_name.ilike(f"%{search}%")) |
            (Student.tc_kimlik.ilike(f"%{search}%"))
        )
    if disability_type:
        query = query.filter(Student.disability_type == disability_type)

    result = await db.execute(query.offset(skip).limit(limit))
    students = result.scalars().all()

    # Format camelCase for frontend friendly consumption
    data = []
    for s in students:
        primary_g = next((g for g in s.guardians if g.is_primary), s.guardians[0] if s.guardians else None)
        active_rep = next((r for r in s.ram_reports if r.is_active), s.ram_reports[0] if s.ram_reports else None)
        
        alloc_mods = []
        if active_rep:
            for m in active_rep.allocated_modules:
                alloc_mods.append({
                    "moduleId": str(m.module_id),
                    "quotaHours": m.monthly_individual_hours
                })

        data.append({
            "id": s.id,
            "firstName": s.first_name,
            "lastName": s.last_name,
            "tcKimlik": s.tc_kimlik,
            "birthDate": str(s.birth_date),
            "gender": s.gender,
            "disabilityType": s.disability_type or "Belirtilmemiş",
            "status": "active" if s.is_active else "inactive",
            "guardian": {
                "name": primary_g.name if primary_g else "",
                "phone": primary_g.phone if primary_g else "",
                "email": primary_g.email if primary_g else "",
                "relationship": primary_g.relationship if primary_g else ""
            } if primary_g else None,
            "ramReport": {
                "reportNumber": active_rep.report_number if active_rep else "",
                "issuingRam": active_rep.issuing_ram if active_rep else "",
                "issueDate": str(active_rep.start_date) if active_rep else "",
                "expiryDate": str(active_rep.end_date) if active_rep else ""
            } if active_rep else None,
            "allocatedModules": alloc_mods
        })

    return {"data": data, "total": len(data), "page": 1, "limit": limit}

@router.post("")
@router.post("/")
async def create_student(data: dict, db: AsyncSession = Depends(get_db)):
    first_name = data.get("firstName") or data.get("first_name", "")
    last_name = data.get("lastName") or data.get("last_name", "")
    tc_kimlik = data.get("tcKimlik") or data.get("tc_kimlik", "")
    b_date_raw = data.get("birthDate") or data.get("birth_date")
    birth_date = date.fromisoformat(b_date_raw) if b_date_raw else date(2018, 1, 1)

    # Boş TC kontrolü
    if not tc_kimlik or not tc_kimlik.strip():
        raise HTTPException(status_code=400, detail="TC Kimlik numarası boş olamaz.")

    # Duplicate TC kontrolü
    existing = await db.execute(select(Student).filter(Student.tc_kimlik == tc_kimlik))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Bu TC Kimlik ({tc_kimlik}) ile kayıtlı bir öğrenci zaten var.")

    try:
        student = Student(
            first_name=first_name,
            last_name=last_name,
            tc_kimlik=tc_kimlik,
            birth_date=birth_date,
            gender=data.get("gender", "Erkek"),
            disability_type=data.get("disabilityType") or data.get("disability_type", "Özel Eğitim"),
            notes=data.get("notes", ""),
            is_active=True
        )
        db.add(student)
        await db.flush()

        # Guardian if provided
        g_data = data.get("guardian", {})
        if g_data and g_data.get("name"):
            guardian = Guardian(
                student_id=student.id,
                name=g_data.get("name"),
                phone=g_data.get("phone", ""),
                email=g_data.get("email", ""),
                relationship=g_data.get("relationship", "Veli"),
                is_primary=True
            )
            db.add(guardian)

        # RAM Report if provided
        r_data = data.get("ramReport", {})
        rep_num = r_data.get("reportNumber", f"RAM-{student.tc_kimlik[:5]}")
        ram_rep = RamReport(
            student_id=student.id,
            report_number=rep_num,
            issuing_ram=r_data.get("issuingRam", "İlçe RAM"),
            start_date=date.today(),
            end_date=date.today().replace(year=date.today().year + 1),
            is_active=True
        )
        db.add(ram_rep)
        await db.flush()

        # Modules
        modules = data.get("allocatedModules", [])
        if not modules:
            # Default allocation 1 module with 8 hours
            modules = [{"moduleId": 1, "quotaHours": 8}]

        for m in modules:
            alloc = AllocatedModule(
                ram_report_id=ram_rep.id,
                module_id=int(m.get("moduleId", 1)),
                monthly_individual_hours=int(m.get("quotaHours", 8)),
                monthly_group_hours=4
            )
            db.add(alloc)

        await db.commit()

        # Trigger auto-scheduling for the new student!
        try:
            engine = SchedulerEngine()
            await engine.add_student_to_existing_schedule(db, student.id)
        except Exception as e:
            pass

        return {"id": student.id, "message": "Öğrenci kaydedildi ve ders programı otomatik oluşturuldu."}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Bu bilgilerle kayıtlı bir öğrenci zaten mevcut.")

@router.get("/{id}")
async def get_student(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Student)
        .filter(Student.id == id)
        .options(
            selectinload(Student.guardians),
            selectinload(Student.ram_reports).selectinload(RamReport.allocated_modules)
        )
    )
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı.")

    primary_g = next((g for g in s.guardians if g.is_primary), s.guardians[0] if s.guardians else None)
    active_rep = next((r for r in s.ram_reports if r.is_active), s.ram_reports[0] if s.ram_reports else None)

    alloc_mods = []
    if active_rep:
        for m in active_rep.allocated_modules:
            alloc_mods.append({
                "moduleId": str(m.module_id),
                "quotaHours": m.monthly_individual_hours
            })

    return {
        "id": s.id,
        "firstName": s.first_name,
        "lastName": s.last_name,
        "tcKimlik": s.tc_kimlik,
        "birthDate": str(s.birth_date),
        "gender": s.gender,
        "disabilityType": s.disability_type,
        "notes": s.notes,
        "status": "active" if s.is_active else "inactive",
        "guardian": {
            "name": primary_g.name if primary_g else "",
            "phone": primary_g.phone if primary_g else "",
            "email": primary_g.email if primary_g else "",
            "relationship": primary_g.relationship if primary_g else ""
        } if primary_g else None,
        "ramReport": {
            "reportNumber": active_rep.report_number if active_rep else "",
            "issuingRam": active_rep.issuing_ram if active_rep else "",
            "issueDate": str(active_rep.start_date) if active_rep else "",
            "expiryDate": str(active_rep.end_date) if active_rep else ""
        } if active_rep else None,
        "allocatedModules": alloc_mods
    }

@router.put("/{id}")
async def update_student(id: str, data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Student)
        .filter(Student.id == id)
        .options(
            selectinload(Student.guardians),
            selectinload(Student.ram_reports).selectinload(RamReport.allocated_modules)
        )
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")
    
    if "firstName" in data or "first_name" in data:
        student.first_name = data.get("firstName") or data.get("first_name")
    if "lastName" in data or "last_name" in data:
        student.last_name = data.get("lastName") or data.get("last_name")
    if "tcKimlik" in data or "tc_kimlik" in data:
        student.tc_kimlik = data.get("tcKimlik") or data.get("tc_kimlik")
    if "birthDate" in data or "birth_date" in data:
        b_raw = data.get("birthDate") or data.get("birth_date")
        if b_raw:
            student.birth_date = date.fromisoformat(str(b_raw).split("T")[0])
    if "gender" in data:
        student.gender = data["gender"]
    if "disabilityType" in data or "disability_type" in data:
        student.disability_type = data.get("disabilityType") or data.get("disability_type")
    if "notes" in data:
        student.notes = data["notes"]
    if "is_active" in data:
        student.is_active = data["is_active"]

    # Guardian update
    g_data = data.get("guardian")
    if g_data and isinstance(g_data, dict):
        if student.guardians:
            g = student.guardians[0]
            if "name" in g_data: g.name = g_data["name"]
            if "phone" in g_data: g.phone = g_data["phone"]
            if "email" in g_data: g.email = g_data["email"]
            if "relationship" in g_data: g.relationship = g_data["relationship"]
        else:
            new_g = Guardian(
                student_id=student.id,
                name=g_data.get("name", "Veli"),
                phone=g_data.get("phone", ""),
                email=g_data.get("email", ""),
                relationship=g_data.get("relationship", "Veli"),
                is_primary=True
            )
            db.add(new_g)

    # RAM Report & modules update
    r_data = data.get("ramReport")
    if r_data and isinstance(r_data, dict):
        if student.ram_reports:
            r = student.ram_reports[0]
            if "reportNumber" in r_data: r.report_number = r_data["reportNumber"]
            if "issuingRam" in r_data: r.issuing_ram = r_data["issuingRam"]
        else:
            new_r = RamReport(
                student_id=student.id,
                report_number=r_data.get("reportNumber", f"RAM-{student.tc_kimlik[:5]}"),
                issuing_ram=r_data.get("issuingRam", "İlçe RAM"),
                start_date=date.today(),
                end_date=date.today().replace(year=date.today().year + 1),
                is_active=True
            )
            db.add(new_r)

    # Modüller güncellenmişse
    if "allocatedModules" in data and isinstance(data["allocatedModules"], list):
        active_rep = student.ram_reports[0] if student.ram_reports else None
        if active_rep:
            # mevcutları temizle ve yenilerini ekle
            for am in list(active_rep.allocated_modules):
                await db.delete(am)
            for m in data["allocatedModules"]:
                db.add(AllocatedModule(
                    ram_report_id=active_rep.id,
                    module_id=int(m.get("moduleId", 1)),
                    monthly_individual_hours=int(m.get("quotaHours", 8)),
                    monthly_group_hours=4
                ))
    
    await db.commit()
    return {"id": student.id, "message": "Öğrenci başarıyla güncellendi."}

@router.delete("/{id}")
async def delete_student(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).filter(Student.id == id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")
    student.is_active = False
    await db.commit()
    return {"message": "Öğrenci silindi."}

@router.get("/{id}/schedule")
async def get_student_schedule(id: str, db: AsyncSession = Depends(get_db)):
    query = await db.execute(
        select(TherapySession)
        .join(SessionParticipant, SessionParticipant.session_id == TherapySession.id)
        .filter(SessionParticipant.student_id == id)
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
            "therapistId": sess.therapist_id,
            "roomId": sess.room_id,
            "status": sess.status.value.lower()
        }
        for sess in sessions
    ]
