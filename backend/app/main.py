import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.router import api_router
from app.database import engine, Base, async_session_maker
from app.seed import seed_all_data
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ÖREM - Özel Eğitim ve Rehabilitasyon Yönetim Sistemi API",
    description="Özel eğitim merkezleri için akıllı ders programı ve rehabilitasyon takip sistemi",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

# --- Static file serving for production deployment ---
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

if STATIC_DIR.exists():
    # Serve static assets (JS, CSS, images, etc.)
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="static-assets")

    # Catch-all: serve index.html for any non-API route (SPA client-side routing)
    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        # If the requested file exists in static dir, serve it directly
        file_path = STATIC_DIR / full_path
        if full_path and file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        # Otherwise serve index.html for client-side routing
        return FileResponse(STATIC_DIR / "index.html")

@app.on_event("startup")
async def startup():
    from sqlalchemy import text
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Check and migrate columns if needed
        try:
            if "sqlite" in str(engine.url):
                cols_res = await conn.execute(text("PRAGMA table_info(students)"))
                cols = [row[1] for row in cols_res.fetchall()]
                if "preferred_therapist_id" not in cols:
                    await conn.execute(text("ALTER TABLE students ADD COLUMN preferred_therapist_id VARCHAR"))
                    logger.info("Migrated students table: added preferred_therapist_id column.")

                t_cols_res = await conn.execute(text("PRAGMA table_info(therapists)"))
                t_cols = [row[1] for row in t_cols_res.fetchall()]
                if "branch" not in t_cols:
                    await conn.execute(text("ALTER TABLE therapists ADD COLUMN branch VARCHAR"))
                    logger.info("Migrated therapists table: added branch column.")

                am_cols_res = await conn.execute(text("PRAGMA table_info(allocated_modules)"))
                am_cols = [row[1] for row in am_cols_res.fetchall()]
                if "program_name" not in am_cols:
                    await conn.execute(text("ALTER TABLE allocated_modules ADD COLUMN program_name VARCHAR"))
                if "module_name" not in am_cols:
                    await conn.execute(text("ALTER TABLE allocated_modules ADD COLUMN module_name VARCHAR"))
            else:
                # PostgreSQL migrations
                await conn.execute(text("ALTER TABLE students ADD COLUMN IF NOT EXISTS preferred_therapist_id VARCHAR"))
                await conn.execute(text("ALTER TABLE therapists ADD COLUMN IF NOT EXISTS branch VARCHAR"))
                await conn.execute(text("ALTER TABLE allocated_modules ADD COLUMN IF NOT EXISTS program_name VARCHAR"))
                await conn.execute(text("ALTER TABLE allocated_modules ADD COLUMN IF NOT EXISTS module_name VARCHAR"))
                logger.info("PostgreSQL table columns verified.")
        except Exception as e:
            logger.warning(f"Schema migration notice: {e}")
    
    # Run seed data
    async with async_session_maker() as db:
        try:
            await seed_all_data(db)
        except Exception as e:
            logger.error(f"Error seeding data: {e}", exc_info=True)
            
    logger.info("ÖREM API Startup complete.")
