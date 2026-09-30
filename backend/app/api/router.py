from fastapi import APIRouter
from app.api import auth, students, therapists, modules, rooms, sessions, schedule, iep, dashboard, reports

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(therapists.router, prefix="/therapists", tags=["therapists"])
api_router.include_router(modules.router, prefix="/modules", tags=["modules"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(schedule.router, prefix="/schedule", tags=["schedule"])
api_router.include_router(iep.router, prefix="/iep", tags=["iep"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
