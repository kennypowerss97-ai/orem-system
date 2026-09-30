from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.therapy_module import TherapyModule

router = APIRouter()

MODULE_COLORS = {
    1: "#1890ff", # Dil ve Konuşma (Mavi)
    2: "#52c41a", # Fizyoterapi (Yeşil)
    3: "#fa8c16", # Özel Öğrenme (Turuncu)
    4: "#722ed1", # Otizm (Mor)
    5: "#eb2f96", # Zihinsel (Pembe)
    6: "#13c2c2", # İşitme (Camgöbeği)
    7: "#faad14", # Görme (Sarı)
}

@router.get("")
@router.get("/")
async def get_modules(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TherapyModule).order_by(TherapyModule.id))
    modules = result.scalars().all()
    return [
        {
            "id": str(m.id),
            "name": m.title,
            "code": m.code,
            "duration": m.default_duration_minutes,
            "isGroupEligible": m.is_group_eligible,
            "color": MODULE_COLORS.get(m.id, "#1890ff")
        }
        for m in modules
    ]

@router.post("")
@router.post("/")
async def create_module(data: dict, db: AsyncSession = Depends(get_db)):
    code = (data.get("code") or data.get("name", "")).upper().replace(" ", "_")[:20]
    import random
    if not code:
        code = f"BRANS_{random.randint(100, 999)}"
    
    # Check if code exists
    existing = await db.execute(select(TherapyModule).filter(TherapyModule.code == code))
    if existing.scalar_one_or_none():
        code = f"{code[:15]}_{random.randint(10, 99)}"

    mod = TherapyModule(
        code=code,
        title=data.get("name") or data.get("title", "Yeni Branş"),
        default_duration_minutes=int(data.get("duration", 45)),
        is_group_eligible=bool(data.get("isGroupEligible", True))
    )
    db.add(mod)
    await db.commit()
    await db.refresh(mod)
    return {
        "id": str(mod.id),
        "name": mod.title,
        "code": mod.code,
        "duration": mod.default_duration_minutes,
        "isGroupEligible": mod.is_group_eligible,
        "color": MODULE_COLORS.get(mod.id, "#1890ff"),
        "message": "Branş başarıyla eklendi."
    }

@router.put("/{id}")
async def update_module(id: int, data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TherapyModule).filter(TherapyModule.id == id))
    mod = result.scalar_one_or_none()
    from fastapi import HTTPException
    if not mod:
        raise HTTPException(status_code=404, detail="Branş bulunamadı")

    if "name" in data or "title" in data:
        mod.title = data.get("name") or data.get("title")
    if "code" in data:
        mod.code = data["code"]
    if "duration" in data:
        mod.default_duration_minutes = int(data["duration"])
    if "isGroupEligible" in data:
        mod.is_group_eligible = bool(data["isGroupEligible"])

    await db.commit()
    return {"message": "Branş bilgileri güncellendi.", "id": str(mod.id)}

@router.delete("/{id}")
async def delete_module(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TherapyModule).filter(TherapyModule.id == id))
    mod = result.scalar_one_or_none()
    from fastapi import HTTPException
    if not mod:
        raise HTTPException(status_code=404, detail="Branş bulunamadı")

    await db.delete(mod)
    await db.commit()
    return {"message": "Branş silindi."}

