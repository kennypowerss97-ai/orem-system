from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.room import Room, RoomModule

router = APIRouter()

@router.get("/")
async def get_rooms(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Room)
        .options(selectinload(Room.supported_modules))
    )
    rooms = result.scalars().all()
    data = []
    for r in rooms:
        supp = [str(rm.module_id) for rm in r.supported_modules]
        data.append({
            "id": str(r.id),
            "name": r.name,
            "code": r.code,
            "capacity": r.max_capacity,
            "supportedModules": supp,
            "status": "active" if r.is_active else "maintenance"
        })
    return {"data": data, "total": len(data), "page": 1, "limit": 100}

@router.post("/")
async def create_room(data: dict, db: AsyncSession = Depends(get_db)):
    room = Room(
        name=data.get("name", "Yeni Oda"),
        code=data.get("code", "ODA-00"),
        max_capacity=int(data.get("capacity", 1)),
        is_active=True
    )
    db.add(room)
    await db.flush()

    for mod_id in data.get("supportedModules", []):
        rm = RoomModule(room_id=room.id, module_id=int(mod_id))
        db.add(rm)

    await db.commit()
    return {"id": str(room.id), "message": "Oda oluşturuldu."}

@router.put("/{id}")
async def update_room(id: int, data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Room).filter(Room.id == id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Oda bulunamadı")
    
    if "name" in data:
        room.name = data["name"]
    if "code" in data:
        room.code = data["code"]
    if "capacity" in data:
        room.max_capacity = int(data["capacity"])
    
    await db.commit()
    return {"id": str(room.id), "message": "Oda güncellendi."}
