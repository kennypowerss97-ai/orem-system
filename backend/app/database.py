from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

import urllib.parse
import ssl

db_url = settings.DATABASE_URL.strip()

# Render / Supabase / Neon often provide postgres:// instead of postgresql+asyncpg://
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

connect_args = {}
if "postgresql+asyncpg" in db_url:
    url_parts = urllib.parse.urlsplit(db_url)
    query_params = urllib.parse.parse_qs(url_parts.query)

    # Handle SSL
    ssl_mode = query_params.get("sslmode", [""])[0].lower()
    if ssl_mode in ("require", "verify-ca", "verify-full") or "ssl" in query_params:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ctx

    # Strip parameters that asyncpg doesn't accept
    unsupported = {"channel_binding", "sslmode", "target_session_attrs", "gssencmode"}
    filtered_query = {k: v for k, v in query_params.items() if k.lower() not in unsupported}
    new_query = urllib.parse.urlencode(filtered_query, doseq=True)

    db_url = urllib.parse.urlunsplit((
        url_parts.scheme,
        url_parts.netloc,
        url_parts.path,
        new_query,
        url_parts.fragment
    ))

engine = create_async_engine(db_url, echo=False, connect_args=connect_args)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
async_session_maker = AsyncSessionLocal
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

