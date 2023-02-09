import asyncio

from model import Base
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine


async def create_table(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# define the engine that connects to the database
engine = create_async_engine("sqlite+aiosqlite:///database.db")
# define the sessionmaker that creates a "session", on which database operations are performed
# See https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#synopsis-orm for further details
async_session = async_sessionmaker(engine, expire_on_commit=False)
# create tables related to Base. if they already exist, this coroutine does nothing.
asyncio.run(create_table(engine=engine))
