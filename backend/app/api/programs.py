from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.database import get_db
from app.models.education_program import EducationProgram, EducationProgramModule

router = APIRouter()

MEB_STANDARD_PROGRAMS = [
    {
        "name": "Zihinsel Engelli Bireyler Destek Eğitim Programı",
        "code": "ZIHINSEL_PROGRAM",
        "color": "#eb2f96",
        "description": "Zihinsel yetersizliği olan bireylerin gelişimsel ve bilişsel destek eğitimi programı",
        "individualHours": 8,
        "groupHours": 4,
        "modules": [
            {"name": "Öz Bakım Becerileri", "description": "Kişisel bakım, giyinme, tuvalet ve hijyen", "duration": 45, "isGroup": False},
            {"name": "Günlük Yaşam Becerileri", "description": "Ev içi ve çevresel günlük yaşam uygulamaları", "duration": 45, "isGroup": True},
            {"name": "Dil Konuşma ve Alternatif İletişim Becerileri", "description": "Alıcı/ifade edici dil ve iletişim araçları", "duration": 45, "isGroup": True},
            {"name": "Bilişsel Beceriler ve Hazırlık", "description": "Kavramlar, eşleme, sınıflandırma ve problem çözme", "duration": 45, "isGroup": True},
            {"name": "Psikomotor ve Hareket Becerileri", "description": "Kaba ve ince motor koordinasyon", "duration": 45, "isGroup": True},
            {"name": "Sosyal Hayat Becerileri", "description": "Toplumsal kurallar ve sosyal etkileşim", "duration": 45, "isGroup": True},
            {"name": "Matematik Becerileri", "description": "Sayılar, işlemler ve pratik matematik", "duration": 45, "isGroup": True},
            {"name": "Türkçe (Okuma - Yazma)", "description": "Temel okuma-yazma ve anlama becerileri", "duration": 45, "isGroup": True}
        ]
    },
    {
        "name": "Yaygın Gelişimsel Bozukluklar (Otizm Spektrum) Destek Eğitim Programı",
        "code": "OTIZM_PROGRAM",
        "color": "#722ed1",
        "description": "Otizm spektrum bozukluğu olan bireylerin erken müdahale ve sosyal adaptasyon programı",
        "individualHours": 8,
        "groupHours": 4,
        "modules": [
            {"name": "Eşleme Becerileri", "description": "Nesne, resim ve sembol eşleme", "duration": 45, "isGroup": False},
            {"name": "Taklit Becerileri", "description": "Kaba motor, ince motor ve ses taklidi", "duration": 45, "isGroup": False},
            {"name": "Yönerge Takip Becerileri", "description": "Tekli ve çoklu yönergeleri uygulama", "duration": 45, "isGroup": True},
            {"name": "Ortak Dikkat ve Etkileşim", "description": "Göz teması ve ortak dikkatin geliştirilmesi", "duration": 45, "isGroup": True},
            {"name": "Alıcı Dil Becerileri", "description": "Sözlü uyaranları anlama ve yanıt verme", "duration": 45, "isGroup": True},
            {"name": "İfade Edici Dil Becerileri", "description": "Sözlü veya PECS/alternatif ifade", "duration": 45, "isGroup": True},
            {"name": "Oyun ve Sosyal Beceriler", "description": "Sembolik oyun ve akran iletişimi", "duration": 45, "isGroup": True},
            {"name": "Günlük Yaşam ve Öz Bakım", "description": "Bağımsız yaşam ve rutinler", "duration": 45, "isGroup": True}
        ]
    },
    {
        "name": "Özel Öğrenme Güçlüğü (Disleksi vb.) Destek Eğitim Programı",
        "code": "OZEL_OGRENME_PROGRAM",
        "color": "#fa8c16",
        "description": "Disleksi, disgrafi ve diskalkuli tanılı bireyler için akademik destek programı",
        "individualHours": 8,
        "groupHours": 4,
        "modules": [
            {"name": "Öğrenmeye Hazırlık ve Duyusal Algı", "description": "Görsel-işitsel algı ve mekan algısı", "duration": 45, "isGroup": True},
            {"name": "Okuma Becerileri ve Akıcılık", "description": "Fonolojik farkındalık, harf-ses uyumu", "duration": 45, "isGroup": True},
            {"name": "Yazma Becerileri (Disgrafi Desteği)", "description": "El yazısı, heceleme ve yazılı ifade", "duration": 45, "isGroup": True},
            {"name": "Matematik Becerileri (Diskalkuli Desteği)", "description": "Sayı hissi, mantıksal problem çözme", "duration": 45, "isGroup": True},
            {"name": "Dikkat, Bellek ve Çalışma Becerileri", "description": "Kısa süreli bellek ve planlama becerileri", "duration": 45, "isGroup": True}
        ]
    },
    {
        "name": "Bedensel Engelli Bireyler (Fizyoterapi) Destek Eğitim Programı",
        "code": "BEDENSEL_PROGRAM",
        "color": "#52c41a",
        "description": "Serebral Palsi, spina bifida ve motor yetersizlikleri olan bireyler için rehabilitasyon",
        "individualHours": 8,
        "groupHours": 0,
        "modules": [
            {"name": "Kaba Motor Becerileri", "description": "Denge, oturma, emekleme ve yürüme", "duration": 45, "isGroup": False},
            {"name": "İnce Motor ve El Becerileri", "description": "Kavrama, bırakma ve manipülatif el fonksiyonları", "duration": 45, "isGroup": False},
            {"name": "Günlük Yaşam Aktiviteleri ve Bağımsızlık", "description": "Transfer, pozisyonlama ve yardımcı cihaz kullanımı", "duration": 45, "isGroup": False},
            {"name": "Hareket ve Fiziksel Uygunluk", "description": "Eklem hareket açıklığı ve kas kuvvetlendirme", "duration": 45, "isGroup": False}
        ]
    },
    {
        "name": "Dil ve Konuşma Güçlüğü Destek Eğitim Programı",
        "code": "DIL_KONUSMA_PROGRAM",
        "color": "#13c2c2",
        "description": "Artikülasyon, kekemelik, apraksi ve gecikmiş konuşma destek programı",
        "individualHours": 8,
        "groupHours": 0,
        "modules": [
            {"name": "Sesletim ve Sesbilgisi (Artikülasyon / Fonoloji)", "description": "Ses üretim hataları ve fonolojik süreçler", "duration": 45, "isGroup": False},
            {"name": "Akıcılık Becerileri (Kekemelik / Hızlı Konuşma)", "description": "Konuşma akıcılığı ve nefes teknikleri", "duration": 45, "isGroup": False},
            {"name": "Ses Bozuklukları Terapisi", "description": "Ses hijyeni ve ses perdesi/şiddeti kontrolü", "duration": 45, "isGroup": False},
            {"name": "Alıcı ve İfade Edici Dil Becerileri", "description": "Kelime dağarcığı ve cümle yapısı oluşturma", "duration": 45, "isGroup": False}
        ]
    },
    {
        "name": "İşitme Engelli Bireyler Destek Eğitim Programı",
        "code": "ISITME_PROGRAM",
        "color": "#fa541c",
        "description": "Koklear implant ve işitme cihazı kullanan bireyler için işitsel-sözel eğitim",
        "individualHours": 8,
        "groupHours": 4,
        "modules": [
            {"name": "İşitsel Algı ve Fark Etme Becerileri", "description": "Sesin varlığı, ayırt edilmesi ve lokalizasyonu", "duration": 45, "isGroup": True},
            {"name": "Dil ve İletişim Becerileri", "description": "Doğal işitsel-sözel dil gelişimi", "duration": 45, "isGroup": True},
            {"name": "Sosyal ve Akademik İletişim", "description": "Akran iletişimi ve okul başarısı desteği", "duration": 45, "isGroup": True}
        ]
    },
    {
        "name": "Görme Engelli Bireyler Destek Eğitim Programı",
        "code": "GORME_PROGRAM",
        "color": "#a0d911",
        "description": "Az gören ve görmeyen bireyler için bağımsız hareket ve kabartma yazı eğitimi",
        "individualHours": 8,
        "groupHours": 4,
        "modules": [
            {"name": "Bağımsız Hareket ve Beyaz Baston Becerileri", "description": "Yön bulma, baston teknikleri ve bağımsız dolaşım", "duration": 45, "isGroup": False},
            {"name": "Braille (Kabartma) Okuma ve Yazma", "description": "Braille alfabesi ve tablet/daktilo kullanımı", "duration": 45, "isGroup": True},
            {"name": "Günlük Yaşam ve Duyusal Algı Geliştirme", "description": "Dokunsal, işitsel ve koku ipuçlarını kullanma", "duration": 45, "isGroup": True}
        ]
    },
    {
        "name": "Duyu Bütünleme ve Ergoterapi Destek Programı",
        "code": "ERGOTERAPI_PROGRAM",
        "color": "#1890ff",
        "description": "Duyusal regülasyon, vücut farkındalığı ve günlük yaşama katılım desteği",
        "individualHours": 8,
        "groupHours": 0,
        "modules": [
            {"name": "Duyusal İşleme ve Regülasyon", "description": "Vestibüler, proprioseptif ve dokunsal uyaran adaptasyonu", "duration": 45, "isGroup": False},
            {"name": "Postüral Kontrol ve Praksis Becerileri", "description": "Hareket planlama ve gövde kontrolü", "duration": 45, "isGroup": False},
            {"name": "Okul ve Günlük Yaşama Katılım Becerileri", "description": "İnce beceriler, dikkat süresi ve sınıf içi regülasyon", "duration": 45, "isGroup": False}
        ]
    }
]

@router.get("")
@router.get("/")
async def list_education_programs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(EducationProgram)
        .options(selectinload(EducationProgram.modules))
        .order_by(EducationProgram.id)
    )
    programs = result.scalars().all()

    data = []
    for p in programs:
        mods = [
            {
                "id": m.id,
                "name": m.name,
                "code": m.code or "",
                "description": m.description or "",
                "isGroupEligible": m.is_group_eligible,
                "durationMinutes": m.duration_minutes,
                "isActive": m.is_active
            }
            for m in p.modules
        ]
        data.append({
            "id": p.id,
            "name": p.name,
            "code": p.code,
            "description": p.description or "",
            "color": p.color or "#1890ff",
            "defaultIndividualHours": p.default_individual_hours,
            "defaultGroupHours": p.default_group_hours,
            "isActive": p.is_active,
            "modules": mods,
            "moduleCount": len(mods)
        })
    return data

@router.post("")
@router.post("/")
async def create_education_program(data: dict, db: AsyncSession = Depends(get_db)):
    name = (data.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Program adı zorunludur.")
    code = (data.get("code") or name.upper().replace(" ", "_")[:25]).strip()

    existing = await db.execute(select(EducationProgram).filter(EducationProgram.name == name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Bu isimde bir Destek Eğitim Programı zaten mevcut.")

    prog = EducationProgram(
        name=name,
        code=code,
        description=data.get("description", ""),
        color=data.get("color", "#1890ff"),
        default_individual_hours=int(data.get("defaultIndividualHours", 8)),
        default_group_hours=int(data.get("defaultGroupHours", 4)),
        is_active=bool(data.get("isActive", True))
    )
    db.add(prog)
    await db.flush()

    # If modules passed
    raw_modules = data.get("modules", [])
    for rm in raw_modules:
        m_name = rm.get("name") if isinstance(rm, dict) else str(rm)
        if m_name:
            m_obj = EducationProgramModule(
                program_id=prog.id,
                name=m_name,
                code=rm.get("code") if isinstance(rm, dict) else None,
                description=rm.get("description") if isinstance(rm, dict) else "",
                is_group_eligible=bool(rm.get("isGroupEligible", True)) if isinstance(rm, dict) else True,
                duration_minutes=int(rm.get("durationMinutes", 45)) if isinstance(rm, dict) else 45,
                is_active=True
            )
            db.add(m_obj)

    await db.commit()
    return {"id": prog.id, "message": "Destek Eğitim Programı başarıyla oluşturuldu."}

@router.put("/{id}")
async def update_education_program(id: int, data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EducationProgram).filter(EducationProgram.id == id))
    prog = result.scalar_one_or_none()
    if not prog:
        raise HTTPException(status_code=404, detail="Program bulunamadı.")

    if "name" in data and data["name"]:
        prog.name = data["name"].strip()
    if "code" in data and data["code"]:
        prog.code = data["code"].strip()
    if "description" in data:
        prog.description = data["description"]
    if "color" in data:
        prog.color = data["color"]
    if "defaultIndividualHours" in data:
        prog.default_individual_hours = int(data["defaultIndividualHours"])
    if "defaultGroupHours" in data:
        prog.default_group_hours = int(data["defaultGroupHours"])
    if "isActive" in data:
        prog.is_active = bool(data["isActive"])

    await db.commit()
    return {"message": "Destek Eğitim Programı güncellendi.", "id": prog.id}

@router.delete("/{id}")
async def delete_education_program(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EducationProgram).filter(EducationProgram.id == id))
    prog = result.scalar_one_or_none()
    if not prog:
        raise HTTPException(status_code=404, detail="Program bulunamadı.")

    await db.delete(prog)
    await db.commit()
    return {"message": "Destek Eğitim Programı ve tüm alt modülleri silindi."}

@router.post("/{id}/modules")
async def add_module_to_program(id: int, data: dict, db: AsyncSession = Depends(get_db)):
    name = (data.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Modül adı zorunludur.")

    mod = EducationProgramModule(
        program_id=id,
        name=name,
        code=data.get("code"),
        description=data.get("description", ""),
        is_group_eligible=bool(data.get("isGroupEligible", True)),
        duration_minutes=int(data.get("durationMinutes", 45)),
        is_active=True
    )
    db.add(mod)
    await db.commit()
    await db.refresh(mod)
    return {
        "id": mod.id,
        "programId": mod.program_id,
        "name": mod.name,
        "description": mod.description,
        "isGroupEligible": mod.is_group_eligible,
        "durationMinutes": mod.duration_minutes,
        "message": "Alt modül başarıyla eklendi."
    }

@router.put("/modules/{module_id}")
async def update_program_module(module_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EducationProgramModule).filter(EducationProgramModule.id == module_id))
    mod = result.scalar_one_or_none()
    if not mod:
        raise HTTPException(status_code=404, detail="Modül bulunamadı.")

    if "name" in data and data["name"]:
        mod.name = data["name"].strip()
    if "code" in data:
        mod.code = data["code"]
    if "description" in data:
        mod.description = data["description"]
    if "isGroupEligible" in data:
        mod.is_group_eligible = bool(data["isGroupEligible"])
    if "durationMinutes" in data:
        mod.duration_minutes = int(data["durationMinutes"])
    if "isActive" in data:
        mod.is_active = bool(data["isActive"])

    await db.commit()
    return {"message": "Modül güncellendi.", "id": mod.id}

@router.delete("/modules/{module_id}")
async def delete_program_module(module_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EducationProgramModule).filter(EducationProgramModule.id == module_id))
    mod = result.scalar_one_or_none()
    if not mod:
        raise HTTPException(status_code=404, detail="Modül bulunamadı.")

    await db.delete(mod)
    await db.commit()
    return {"message": "Modül silindi."}
