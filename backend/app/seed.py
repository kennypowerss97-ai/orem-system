import logging
from datetime import date, time, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.core.security import get_password_hash
from app.models.user import User, RoleEnum
from app.models.therapy_module import TherapyModule
from app.models.room import Room, RoomModule
from app.models.therapist import Therapist, TherapistSpecialization, TherapistAvailability
from app.models.student import Student, Guardian, RamReport, AllocatedModule
from app.services.scheduler_engine import SchedulerEngine

logger = logging.getLogger(__name__)

async def seed_all_data(db: AsyncSession):
    # 1. Admin User
    admin_check = await db.execute(select(User).filter(User.username == "admin"))
    if not admin_check.scalars().first():
        admin = User(
            username="admin",
            email="admin@orem.com",
            hashed_password=get_password_hash("admin123"),
            role=RoleEnum.ADMIN,
            is_active=True
        )
        db.add(admin)
        await db.flush()

    # 2. Therapy Modules (MEB Müfredatı)
    modules_data = [
        {"id": 1, "code": "DIL_KONUSMA", "title": "Dil ve Konuşma Güçlüğü Destek Eğitimi", "duration": 45, "group": True},
        {"id": 2, "code": "BEDENSEL_FIZYOTERAPI", "title": "Bedensel Engelli Bireyler (Fizyoterapi) Destek Eğitimi", "duration": 45, "group": False},
        {"id": 3, "code": "OZEL_OGRENME", "title": "Özel Öğrenme Güçlüğü (Disleksi vb.) Destek Eğitimi", "duration": 45, "group": True},
        {"id": 4, "code": "OTIZM", "title": "Yaygın Gelişimsel Bozukluklar (Otizm) Destek Eğitimi", "duration": 45, "group": True},
        {"id": 5, "code": "ZIHINSEL", "title": "Zihinsel Engelli Bireyler Destek Eğitimi", "duration": 45, "group": True},
        {"id": 6, "code": "ISITME", "title": "İşitme Engelli Bireyler Destek Eğitimi", "duration": 45, "group": True},
        {"id": 7, "code": "GORME", "title": "Görme Engelli Bireyler Destek Eğitimi", "duration": 45, "group": True},
    ]

    for m in modules_data:
        m_check = await db.execute(select(TherapyModule).filter(TherapyModule.id == m["id"]))
        if not m_check.scalars().first():
            module = TherapyModule(
                id=m["id"],
                code=m["code"],
                title=m["title"],
                default_duration_minutes=m["duration"],
                is_group_eligible=m["group"]
            )
            db.add(module)
    await db.flush()

    # 3. Rooms
    rooms_data = [
        {"id": 1, "name": "Dil ve Konuşma Odası 1", "code": "DIL-101", "cap": 2, "modules": [1]},
        {"id": 2, "name": "Fizyoterapi & Rehabilitasyon Salonu", "code": "FZY-102", "cap": 4, "modules": [2]},
        {"id": 3, "name": "Bireysel Özel Eğitim Odası 1", "code": "BIR-103", "cap": 2, "modules": [3, 4, 5]},
        {"id": 4, "name": "Bireysel Özel Eğitim Odası 2", "code": "BIR-104", "cap": 2, "modules": [3, 5, 6, 7]},
        {"id": 5, "name": "Duyu Bütünleme ve Motor Beceri Odası", "code": "DUY-105", "cap": 3, "modules": [2, 4, 5]},
    ]

    for r in rooms_data:
        r_check = await db.execute(select(Room).filter(Room.id == r["id"]))
        if not r_check.scalars().first():
            room = Room(id=r["id"], name=r["name"], code=r["code"], max_capacity=r["cap"], is_active=True)
            db.add(room)
            await db.flush()
            for mod_id in r["modules"]:
                rm = RoomModule(room_id=room.id, module_id=mod_id)
                db.add(rm)
    await db.commit()
    logger.info("Seed data initialized: Admin user, MEB modules and Rooms ready.")

