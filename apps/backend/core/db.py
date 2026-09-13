"""Async SQLAlchemy engine, session factory, and declarative base."""

import os
from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")
if not DATABASE_URL.startswith("postgresql+asyncpg://"):
    raise RuntimeError("DATABASE_URL must use the postgresql+asyncpg driver")

DEBUG = os.getenv("DEBUG", "false").strip().lower() in {"1", "true", "yes", "on"}

# echo logs all SQL; enable only in development via DEBUG.
engine = create_async_engine(DATABASE_URL, echo=DEBUG)

# expire_on_commit=False: avoid implicit lazy reloads after commit, which fail in async code.
SessionFactory = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide one database session per request."""
    async with SessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
