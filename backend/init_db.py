import asyncio
from app.database import engine, Base, async_session_maker
from app.seed import seed_all_data

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_maker() as db:
        await seed_all_data(db)
    print("DATABASE INITIALIZED AND SEEDED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(init())
