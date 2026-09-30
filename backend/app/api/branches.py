from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List, Optional

from app.database import get_db
from app.models.branch import TeacherBranch
from app.models.therapist import Therapist

router = APIRouter()

DEFAULT_BRANCHES = [
    {"name": "Özel Eğitim Alanı Öğretmeni", "code": "OZEL_EGITIM", "color": "#1890ff", "description": "Zihin, otizm ve öğrenme güçlüğü alanında özel eğitim uzmanı"},
    {"name": "Zihin Engelliler Öğretmeni", "code": "ZIHIN_ENG", "color": "#722ed1", "description": "Zihinsel yetersizliği olan bireylerin eğitim ve gelişimi"},
    {"name": "Çocuk Gelişimi ve Eğitimi Uzmanı", "code": "COCUK_GELISIM", "color": "#eb2f96", "description": "Erken çocukluk ve gelişimsel değerlendirme ve destek"},
    {"name": "Okul Öncesi Öğretmeni", "code": "OKUL_ONCESI", "color": "#fa8c16", "description": "Okul öncesi temel beceri ve özel eğitim uygulamaları"},
    {"name": "Fizyoterapist (Fizik Tedavi)", "code": "FIZYOTERAPI", "color": "#52c41a", "description": "Kaba/ince motor becerileri ve nöromüsküler rehabilitasyon"},
    {"name": "Dil ve Konuşma Terapisti", "code": "DIL_KONUSMA", "color": "#13c2c2", "description": "Konuşma, ses, artikülasyon ve alternatif iletişim terapisi"},
    {"name": "Psikolog / PDR (Rehberlik)", "code": "PSIKOLOG_PDR", "color": "#2f54eb", "description": "Psikolojik destek, davranış yönetimi ve aile danışmanlığı"},
    {"name": "Ergoterapist (Duyu Bütünleme)", "code": "ERGOTERAPI", "color": "#faad14", "description": "Duyu bütünleme ve günlük yaşam aktivitelerine katılım"},
    {"name": "İşitme Engelliler Öğretmeni", "code": "ISITME_ENG", "color": "#fa541c", "description": "İşitsel algı ve işitme engelliler eğitimi"},
    {"name": "Görme Engelliler Öğretmeni", "code": "GORME_ENG", "color": "#a0d911", "description": "Braille, bağımsız hareket ve az gören eğitimi"},
    {"name": "Beden Eğitimi (Özel Spor)", "code": "BEDEN_EGITIMI", "color": "#096dd9", "description": "Özel beden eğitimi ve fiziksel aktivite desteği"}
]

@router.get("")
@router.get("/")
async def list_branches(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TeacherBranch).order_by(TeacherBranch.id))
    branches = result.scalars().all()

    # Get teacher counts per branch
    counts_query = await db.execute(
        select(Therapist.branch, func.count(Therapist.id))
        .filter(Therapist.is_active == True)
        .group_by(Therapist.branch)
    )
    counts = dict(counts_query.fetchall())

    data = []
    for b in branches:
        data.append({
            "id": b.id,
            "name": b.name,
            "code": b.code,
            "description": b.description or "",
            "color": b.color or "#1890ff",
            "isActive": b.is_active,
            "teacherCount": counts.get(b.name, 0)
        })
    return data

@router.post("")
@router.post("/")
async def create_branch(data: dict, db: AsyncSession = Depends(get_db)):
    name = (data.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Branş adı zorunludur.")
    
    code = (data.get("code") or name.upper().replace(" ", "_")[:20]).strip()
    existing = await db.execute(select(TeacherBranch).filter(TeacherBranch.name == name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Bu isimde bir branş zaten mevcut.")

    branch = TeacherBranch(
        name=name,
        code=code,
        description=data.get("description", ""),
        color=data.get("color", "#1890ff"),
        is_active=bool(data.get("isActive", True))
    )
    db.add(branch)
    await db.commit()
    await db.refresh(branch)
    return {
        "id": branch.id,
        "name": branch.name,
        "code": branch.code,
        "description": branch.description,
        "color": branch.color,
        "isActive": branch.is_active,
        "message": "Öğretmen branşı başarıyla eklendi."
    }

@router.put("/{id}")
async def update_branch(id: int, data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TeacherBranch).filter(TeacherBranch.id == id))
    branch = result.scalar_one_or_none()
    if not branch:
        raise HTTPException(status_code=404, detail="Branş bulunamadı.")

    if "name" in data and data["name"]:
        branch.name = data["name"].strip()
    if "code" in data and data["code"]:
        branch.code = data["code"].strip()
    if "description" in data:
        branch.description = data["description"]
    if "color" in data:
        branch.color = data["color"]
    if "isActive" in data:
        branch.is_active = bool(data["isActive"])

    await db.commit()
    return {"message": "Branş bilgileri güncellendi.", "id": branch.id}

@router.delete("/{id}")
async def delete_branch(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TeacherBranch).filter(TeacherBranch.id == id))
    branch = result.scalar_one_or_none()
    if not branch:
        raise HTTPException(status_code=404, detail="Branş bulunamadı.")

    await db.delete(branch)
    await db.commit()
    return {"message": "Branş silindi."}
