from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()

postgres_password = os.getenv("POSTGRES_PASSWORD")

engine = create_async_engine(f'postgresql+asyncpg://ecommerce:{postgres_password}@localhost:5432/ecommerce', echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass