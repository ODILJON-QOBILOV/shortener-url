import asyncio
from app.database import Base, engine
from app.models import URL

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_db())
