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
