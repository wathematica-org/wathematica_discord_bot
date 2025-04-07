import asyncio
import signal
import sys
import os

from model import Base
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine


async def create_table(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# define the engine that connects to the database

if os.path.exists("/run/secrets/database_url"):
    with open("/run/secrets/database_url") as discord_token_file:
        # Strip the tailing newline character with strip()
        db_url = discord_token_file.readline().strip()
else:
    db_url = os.environ.get("DATABASE_URL")
    if db_url is None:
        raise FileNotFoundError(
            "[NO TOKEN PROVIDED] check docker-compose.yml to see how you can expose token at /run/secrets/database_url"
        )

print("database_url", db_url)
engine = create_async_engine(db_url)
# define the sessionmaker that creates a "session", on which database operations are performed
# See https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#synopsis-orm for further details
async_session = async_sessionmaker(engine, expire_on_commit=False)
# create tables related to Base. if they already exist, this coroutine does nothing.
asyncio.run(create_table(engine=engine))


# define a signal handler to ensure the database connection is closed when the program is terminated
def signal_handler(signal_num, frame):
    loop = asyncio.get_running_loop()
    loop.run_until_complete(engine.dispose())
    sys.exit()


# register signal_handler to be called when the program is TERMinated or INTerrupted
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
