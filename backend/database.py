import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from dotenv import load_dotenv

load_dotenv()

DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()

if DB_TYPE == "mysql":
    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_USER = os.getenv("MYSQL_USER", "memo")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "memopass")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "memo_db")
    DATABASE_URL = f"mysql+aiomysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
    engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), "memo.db")
    DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"
    engine = create_async_engine(DATABASE_URL, echo=False)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

IS_SQLITE = DB_TYPE != "mysql"


async def get_db():
    async with async_session() as session:
        yield session
