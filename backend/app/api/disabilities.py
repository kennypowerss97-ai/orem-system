from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from app.database import get_db
from app.models.disability import DisabilityType

router = APIRouter()

DEFAULT_DISABILITIES = [
    "Otizm Spektrum Bozukluğu",
    "Serebral Palsi (Bedensel)",
    "Özel Öğrenme Güçlüğü (Disleksi)",
    "Dil ve Konuşma Bozukluğu",
    "Zihinsel Yetersizlik",
    "İşitme Yetersizliği",
    "Down Sendromu",
    "Bedensel / Ortopedik Yetersizlik",
    "Görme Yetersizliği",
    "Yaygın Gelişimsel Bozukluk",
    "Dikkat Eksikliği ve Hiperaktivite (DEHB)"
]

@router.get("")
@router.get("/")
async def list_disabilities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(DisabilityType).filter(DisabilityType.is_active == True).order_by(DisabilityType.name)
    )
    items = result.scalars().all()

    # If empty, populate defaults automatically
    if not items:
        for name in DEFAULT_DISABILITIES:
            d = DisabilityType(name=name, description="MEB Standart Tanı", is_active=True)
            db.add(d)
        await db.commit()
        result = await db.execute(
            select(DisabilityType).filter(DisabilityType.is_active == True).order_by(DisabilityType.name)
        )
        items = result.scalars().all()

    return [
        {
            "id": d.id,
            "name": d.name,
            "description": d.description or "",
            "isActive": d.is_active,
            "createdAt": str(d.created_at) if d.created_at else None
        }
        for d in items
    ]

@router.post("")
@router.post("/")
async def create_disability(data: dict, db: AsyncSession = Depends(get_db)):
    name = (data.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Tanı adı boş bırakılamaz.")

    # Check existing
    existing = await db.execute(
        select(DisabilityType).filter(DisabilityType.name.ilike(name))
    )
    exist_obj = existing.scalar_one_or_none()
    if exist_obj:
        if not exist_obj.is_active:
            exist_obj.is_active = True
            exist_obj.description = data.get("description", exist_obj.description)
            await db.commit()
            return {"id": exist_obj.id, "name": exist_obj.name, "message": "Tanı türü yeniden aktif edildi."}
        raise HTTPException(status_code=400, detail="Bu tanı türü zaten mevcut.")

    d = DisabilityType(
        name=name,
        description=data.get("description", ""),
        is_active=True
    )
    db.add(d)
    await db.commit()
    await db.refresh(d)
    return {
        "id": d.id,
        "name": d.name,
        "description": d.description,
        "isActive": d.is_active,
        "message": "Engel / tanı türü başarıyla eklendi."
    }

@router.put("/{id}")
async def update_disability(id: int, data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DisabilityType).filter(DisabilityType.id == id))
    d = result.scalar_one_or_none()
    if not d:
        raise HTTPException(status_code=404, detail="Tanı türü bulunamadı.")

    if "name" in data and data["name"]:
        d.name = data["name"].strip()
    if "description" in data:
        d.description = data["description"]
    if "isActive" in data:
        d.is_active = bool(data["isActive"])

    await db.commit()
    return {"id": d.id, "name": d.name, "message": "Tanı bilgileri güncellendi."}

@router.delete("/{id}")
async def delete_disability(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DisabilityType).filter(DisabilityType.id == id))
    d = result.scalar_one_or_none()
    if not d:
        raise HTTPException(status_code=404, detail="Tanı türü bulunamadı.")

    # Soft delete
    d.is_active = False
    await db.commit()
    return {"message": "Tanı türü silindi."}
