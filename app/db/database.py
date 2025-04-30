from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.declarative import as_declarative
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DEBUG = os.getenv("DEBUG") == "True"

if DEBUG:
    DATABASE_URL = os.getenv("DATABASE_DEBUG_URL")
else:
    DATABASE_URL = os.getenv("DATABASE_URL")

# Создаем асинхронный движок для базы данных
engine = create_async_engine(DATABASE_URL, echo=True, future=True)
# Асинхронная сессия
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

sync_engine = create_engine(DATABASE_URL.replace("+asyncpg", ""), future=True)
SessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)


# Генератор сессий для работы с базой данных
async def get_db():
    async with async_session() as session:
        yield session
