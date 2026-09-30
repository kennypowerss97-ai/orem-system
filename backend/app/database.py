from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

db_url = settings.DATABASE_URL.strip()

# Render / Supabase / Neon often provide postgres:// instead of postgresql+asyncpg://
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# asyncpg prefers ssl=require or sslmode stripped
connect_args = {}
if "postgresql+asyncpg" in db_url:
    if "sslmode=require" in db_url:
        db_url = db_url.replace("sslmode=require", "").rstrip("?&")
        connect_args["ssl"] = "require"
    elif "sslmode=" in db_url:
        import re
        db_url = re.sub(r'[?&]sslmode=[^&]+', '', db_url)

engine = create_async_engine(db_url, echo=False, connect_args=connect_args)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
async_session_maker = AsyncSessionLocal
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

