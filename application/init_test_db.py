from models import Base
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

load_dotenv()

test_engine = create_async_engine(
    url=f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
    + f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/test",
    echo=True,
)


async def create_test_db():
    async with test_engine.begin() as conn:

        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await test_engine.dispose()


asyncio.run(create_test_db())
