import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
load_dotenv()

engine = create_async_engine(
    url=f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}" +
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}" +
        f"/{os.getenv('DB_NAME')}",
    echo=True
)


class Base(DeclarativeBase):
    pass
