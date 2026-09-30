import logging
from datetime import date, time, datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import delete

from app.models.student import Student, RamReport, AllocatedModule
from app.models.therapist import Therapist, TherapistSpecialization, TherapistAvailability
from app.models.room import Room, RoomModule
from app.models.session import TherapySession, SessionParticipant, SessionTypeEnum, SessionStatusEnum
from app.models.therapy_module import TherapyModule

logger = logging.getLogger(__name__)

# Daily time slots: 45 min session + 15 min rest
DAILY_TIME_SLOTS = [
    (time(9, 0), time(9, 45)),
    (time(10, 0), time(10, 45)),
    (time(11, 0), time(11, 45)),
    (time(13, 0), time(13, 45)),
    (time(14, 0), time(14, 45)),
    (time(15, 0), time(15, 45)),
    (time(16, 0), time(16, 45)),
]

class SchedulerEngine:
    """
    Intelligent therapy scheduling engine for ÖREM rehabilitation centers.
    Applies constraint satisfaction heuristics matching:
    - Therapist specializations
    - Room module capabilities
    - Weekly therapist availabilities
    - Student daily maximum session limits (<= 3 hours/day)
    - Anti-collision across therapists, students, and rooms
    """

    async def generate_full_schedule(
        self,
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        clear_existing: bool = True
    ) -> Dict[str, Any]:
        logger.info("Starting automatic schedule generation...")
        
        if not start_date:
            # Default to current week Monday
            today = date.today()
            start_date = today - timedelta(days=today.weekday())
        if not end_date:
            # Default to Friday of the same week
            end_date = start_date + timedelta(days=4)

        if clear_existing:
            # Remove scheduled sessions in the date range
            await db.execute(
                delete(TherapySession).where(
                    TherapySession.session_date >= start_date,
                    TherapySession.session_date <= end_date,
                    TherapySession.status == SessionStatusEnum.SCHEDULED
                )
            )
            await db.commit()

        # Load active students with reports and modules
        students_query = await db.execute(
            select(Student)
            .filter(Student.is_active == True)
            .options(
                selectinload(Student.ram_reports).selectinload(RamReport.allocated_modules)
            )
        )
        students = students_query.scalars().all()

        # Load therapists with specializations and availability
        therapists_query = await db.execute(
            select(Therapist)
            .filter(Therapist.is_active == True)
            .options(
                selectinload(Therapist.specializations),
                selectinload(Therapist.availability)
            )
        )
        therapists = therapists_query.scalars().all()

        # Load rooms with module support
        rooms_query = await db.execute(
            select(Room)
            .filter(Room.is_active == True)
            .options(selectinload(Room.supported_modules))
        )
        rooms = rooms_query.scalars().all()

        # Build occupied tracking state
        # (date, slot_idx) -> set of occupied entity ids
        occupied_therapists: Dict[str, set] = {}
        occupied_students: Dict[str, set] = {}
        occupied_rooms: Dict[str, set] = {}
        student_daily_counts: Dict[str, int] = {} # f"{student_id}_{date}" -> count

        # Load any existing non-scheduled or existing sessions in this range
        existing_sessions_query = await db.execute(
            select(TherapySession)
            .filter(
                TherapySession.session_date >= start_date,
                TherapySession.session_date <= end_date
            )
            .options(selectinload(TherapySession.participants))
        )
        existing_sessions = existing_sessions_query.scalars().all()

        for sess in existing_sessions:
            d_str = str(sess.session_date)
            # Find slot index
            slot_idx = self._find_slot_index(sess.start_time)
            key = f"{d_str}_{slot_idx}"
            occupied_therapists.setdefault(key, set()).add(sess.therapist_id)
            occupied_rooms.setdefault(key, set()).add(sess.room_id)
            for p in sess.participants:
                occupied_students.setdefault(key, set()).add(p.student_id)
                s_key = f"{p.student_id}_{d_str}"
                student_daily_counts[s_key] = student_daily_counts.get(s_key, 0) + 1

        # Create session demands
        # Each allocated module has monthly hours (e.g. 8 hours/month -> ~2 sessions/week)
        sessions_created = 0
        days_in_range = []
        curr = start_date
        while curr <= end_date:
            # Weekdays only (0: Mon, 4: Fri)
            if curr.weekday() < 5:
                days_in_range.append(curr)
            curr += timedelta(days=1)

        for student in students:
            # Gather modules for active ram report
            active_modules = []
            for rep in student.ram_reports:
                if rep.is_active:
                    for alloc in rep.allocated_modules:
                        # Weekly count ~ monthly / 4 (min 1, max 3)
                        weekly_sessions = max(1, alloc.monthly_individual_hours // 4)
                        for _ in range(weekly_sessions):
                            active_modules.append(alloc.module_id)

            # Schedule each demand
            for module_id in active_modules:
                scheduled = self._schedule_single_demand(
                    student=student,
                    module_id=module_id,
                    days_in_range=days_in_range,
                    therapists=therapists,
                    rooms=rooms,
                    occupied_therapists=occupied_therapists,
                    occupied_students=occupied_students,
                    occupied_rooms=occupied_rooms,
                    student_daily_counts=student_daily_counts,
                    db=db
                )
                if scheduled:
                    sessions_created += 1

        await db.commit()
        logger.info(f"Schedule generated successfully. Total sessions created: {sessions_created}")
        return {
            "status": "SUCCESS",
            "sessions_created": sessions_created,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "message": f"{sessions_created} seans başarıyla oluşturuldu ve takvime yerleştirildi."
        }

    async def add_student_to_existing_schedule(
        self,
        db: AsyncSession,
        student_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Incrementally schedules a newly registered student into available timetable gaps.
        """
        if not start_date:
            today = date.today()
            start_date = today - timedelta(days=today.weekday())
        if not end_date:
            end_date = start_date + timedelta(days=4)

        student_query = await db.execute(
            select(Student)
            .filter(Student.id == student_id)
            .options(
                selectinload(Student.ram_reports).selectinload(RamReport.allocated_modules)
            )
        )
        student = student_query.scalar_one_or_none()
        if not student:
            return {"status": "ERROR", "message": "Öğrenci bulunamadı."}

        therapists_query = await db.execute(
            select(Therapist)
            .filter(Therapist.is_active == True)
            .options(
                selectinload(Therapist.specializations),
                selectinload(Therapist.availability)
            )
        )
        therapists = therapists_query.scalars().all()

        rooms_query = await db.execute(
            select(Room)
            .filter(Room.is_active == True)
            .options(selectinload(Room.supported_modules))
        )
        rooms = rooms_query.scalars().all()

        # Build existing occupancy
        occupied_therapists: Dict[str, set] = {}
        occupied_students: Dict[str, set] = {}
        occupied_rooms: Dict[str, set] = {}
        student_daily_counts: Dict[str, int] = {}

        existing_sessions_query = await db.execute(
            select(TherapySession)
            .filter(
                TherapySession.session_date >= start_date,
                TherapySession.session_date <= end_date
            )
            .options(selectinload(TherapySession.participants))
        )
        existing_sessions = existing_sessions_query.scalars().all()

        for sess in existing_sessions:
            d_str = str(sess.session_date)
            slot_idx = self._find_slot_index(sess.start_time)
            key = f"{d_str}_{slot_idx}"
            occupied_therapists.setdefault(key, set()).add(sess.therapist_id)
            occupied_rooms.setdefault(key, set()).add(sess.room_id)
            for p in sess.participants:
                occupied_students.setdefault(key, set()).add(p.student_id)
                s_key = f"{p.student_id}_{d_str}"
                student_daily_counts[s_key] = student_daily_counts.get(s_key, 0) + 1

        days_in_range = []
        curr = start_date
        while curr <= end_date:
            if curr.weekday() < 5:
                days_in_range.append(curr)
            curr += timedelta(days=1)

        active_modules = []
        for rep in student.ram_reports:
            if rep.is_active:
                for alloc in rep.allocated_modules:
                    weekly_sessions = max(1, alloc.monthly_individual_hours // 4)
                    for _ in range(weekly_sessions):
                        active_modules.append(alloc.module_id)

        sessions_created = 0
        for module_id in active_modules:
            scheduled = self._schedule_single_demand(
                student=student,
                module_id=module_id,
                days_in_range=days_in_range,
                therapists=therapists,
                rooms=rooms,
                occupied_therapists=occupied_therapists,
                occupied_students=occupied_students,
                occupied_rooms=occupied_rooms,
                student_daily_counts=student_daily_counts,
                db=db
            )
            if scheduled:
                sessions_created += 1

        await db.commit()
        return {
            "status": "SUCCESS",
            "sessions_created": sessions_created,
            "message": f"Yeni öğrenci için {sessions_created} seans uygun boşluklara yerleştirildi."
        }

    def _schedule_single_demand(
        self,
        student: Student,
        module_id: int,
        days_in_range: List[date],
        therapists: List[Therapist],
        rooms: List[Room],
        occupied_therapists: Dict[str, set],
        occupied_students: Dict[str, set],
        occupied_rooms: Dict[str, set],
        student_daily_counts: Dict[str, int],
        db: AsyncSession
    ) -> bool:
        # Find candidate therapists who have this specialization
        candidate_therapists = [
            t for t in therapists
            if any(s.module_id == module_id for s in t.specializations)
        ]
        if not candidate_therapists:
            candidate_therapists = therapists # Fallback if no exact specialization mapped

        # Find candidate rooms supporting this module
        candidate_rooms = [
            r for r in rooms
            if any(rm.module_id == module_id for rm in r.supported_modules)
        ]
        if not candidate_rooms:
            candidate_rooms = rooms # Fallback to any active room

        # Try to find a collision-free slot
        for current_date in days_in_range:
            d_str = str(current_date)
            s_daily_key = f"{student.id}_{d_str}"
            if student_daily_counts.get(s_daily_key, 0) >= 3:
                # Student reached MEB daily limit of 3 sessions
                continue

            day_of_week = current_date.weekday() + 1 # 1=Mon, 7=Sun

            for slot_idx, (start_t, end_t) in enumerate(DAILY_TIME_SLOTS):
                slot_key = f"{d_str}_{slot_idx}"

                # Check student occupancy
                if student.id in occupied_students.get(slot_key, set()):
                    continue

                # Find an available therapist
                chosen_therapist = None
                for t in candidate_therapists:
                    if t.id in occupied_therapists.get(slot_key, set()):
                        continue
                    # Check therapist availability day/time
                    if t.availability:
                        is_available = any(
                            av.day_of_week == day_of_week and av.start_time <= start_t and av.end_time >= end_t
                            for av in t.availability
                        )
                        if not is_available:
                            continue
                    chosen_therapist = t
                    break

                if not chosen_therapist:
                    continue

                # Find an available room
                chosen_room = None
                for r in candidate_rooms:
                    if r.id in occupied_rooms.get(slot_key, set()):
                        continue
                    chosen_room = r
                    break

                if not chosen_room:
                    continue

                # Successfully found (day, slot, therapist, room)
                occupied_therapists.setdefault(slot_key, set()).add(chosen_therapist.id)
                occupied_students.setdefault(slot_key, set()).add(student.id)
                occupied_rooms.setdefault(slot_key, set()).add(chosen_room.id)
                student_daily_counts[s_daily_key] = student_daily_counts.get(s_daily_key, 0) + 1

                # Create TherapySession and SessionParticipant
                session = TherapySession(
                    module_id=module_id,
                    therapist_id=chosen_therapist.id,
                    room_id=chosen_room.id,
                    session_date=current_date,
                    start_time=start_t,
                    end_time=end_t,
                    session_type=SessionTypeEnum.INDIVIDUAL,
                    status=SessionStatusEnum.SCHEDULED
                )
                db.add(session)
                participant = SessionParticipant(
                    session=session,
                    student_id=student.id,
                    attended=False
                )
                db.add(participant)
                return True

        return False

    def _find_slot_index(self, t: time) -> int:
        for idx, (st, _) in enumerate(DAILY_TIME_SLOTS):
            if st.hour == t.hour and abs(st.minute - t.minute) < 15:
                return idx
        return 0
