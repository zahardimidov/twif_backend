from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import ENGINE
from database.models import Base

engine = create_async_engine(url=ENGINE, echo=False)

async_session = async_sessionmaker(engine)


async def run_database():
    async with engine.begin() as conn:
        #await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
