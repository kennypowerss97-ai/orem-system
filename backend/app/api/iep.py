from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import date

from app.database import get_db
from app.models.iep import IepPlan, IepGoal, ProgressRecord, GoalStatusEnum

router = APIRouter()

@router.get("/plans")
async def get_iep_plans(student_id: str = None, db: AsyncSession = Depends(get_db)):
    query = select(IepPlan).options(selectinload(IepPlan.goals))
    if student_id:
        query = query.filter(IepPlan.student_id == student_id)
    result = await db.execute(query)
    plans = result.scalars().all()
    return [
        {
            "id": p.id,
            "studentId": p.student_id,
            "moduleId": str(p.module_id),
            "startDate": str(p.start_date),
            "endDate": str(p.end_date),
            "goals": [
                {
                    "id": g.id,
                    "description": g.description,
                    "status": g.status.value.lower()
                }
                for g in p.goals
            ]
        }
        for p in plans
    ]

@router.get("/plans/{plan_id}")
async def get_iep_plan(plan_id: str, db: AsyncSession = Depends(get_db)):
    query = select(IepPlan).options(selectinload(IepPlan.goals)).filter(IepPlan.id == plan_id)
    result = await db.execute(query)
    p = result.scalars().first()
    if not p:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {
        "id": p.id,
        "studentId": p.student_id,
        "moduleId": str(p.module_id),
        "startDate": str(p.start_date),
        "endDate": str(p.end_date),
        "goals": [
            {
                "id": g.id,
                "description": g.description,
                "status": g.status.value.lower()
            }
            for g in p.goals
        ]
    }

@router.post("/plans")
async def create_iep_plan(data: dict, db: AsyncSession = Depends(get_db)):
    plan = IepPlan(
        student_id=data["studentId"],
        module_id=int(data["moduleId"]),
        coordinator_therapist_id=data.get("coordinatorTherapistId", "default"),
        start_date=data["startDate"],
        end_date=data["endDate"],
        notes=data.get("notes", "")
    )
    db.add(plan)
    await db.commit()
    return {"id": plan.id, "message": "BEP planı oluşturuldu."}

@router.post("/plans/{plan_id}/goals")
async def add_iep_goal(plan_id: str, data: dict, db: AsyncSession = Depends(get_db)):
    query = select(IepPlan).filter(IepPlan.id == plan_id)
    result = await db.execute(query)
    plan = result.scalars().first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    goal = IepGoal(
        iep_plan_id=plan_id,
        goal_code=data.get("goalCode", "G-01"),
        description=data["description"],
        status=GoalStatusEnum(data.get("status", "NOT_STARTED").upper()),
        sort_order=int(data.get("sortOrder", 0))
    )
    if "targetDate" in data and data["targetDate"]:
        goal.target_date = data["targetDate"]

    db.add(goal)
    await db.commit()
    return {"id": goal.id, "message": "Hedef eklendi."}

@router.put("/plans/{plan_id}/goals/{goal_id}")
async def update_iep_goal(plan_id: str, goal_id: str, data: dict, db: AsyncSession = Depends(get_db)):
    query = select(IepGoal).filter(IepGoal.id == goal_id, IepGoal.iep_plan_id == plan_id)
    result = await db.execute(query)
    goal = result.scalars().first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    if "status" in data:
        goal.status = GoalStatusEnum(data["status"].upper())
    if "description" in data:
        goal.description = data["description"]
        
    await db.commit()
    return {"message": "Hedef güncellendi."}

@router.post("/progress")
async def add_progress_record(data: dict, db: AsyncSession = Depends(get_db)):
    rec = ProgressRecord(
        session_participant_id=data["sessionId"],
        iep_goal_id=data["goalId"],
        performance_score=float(data.get("rating", 3.0)),
        observations=data.get("notes", "")
    )
    db.add(rec)
    await db.commit()
    return {"message": "PKT performansı başarıyla kaydedildi."}

@router.get("/progress/student/{student_id}")
async def get_student_progress(student_id: str, db: AsyncSession = Depends(get_db)):
    query = select(ProgressRecord).join(IepGoal).join(IepPlan).filter(IepPlan.student_id == student_id)
    result = await db.execute(query)
    records = result.scalars().all()
    
    return [
        {
            "id": r.id,
            "sessionId": r.session_participant_id,
            "goalId": r.iep_goal_id,
            "rating": r.performance_score,
            "notes": r.observations,
            "recordedAt": str(r.recorded_at) if r.recorded_at else None
        }
        for r in records
    ]
