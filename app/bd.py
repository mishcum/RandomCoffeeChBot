from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, BigInteger, Text, DateTime, CheckConstraint, ForeignKey
from datetime import datetime
from sqlalchemy.sql import func

from dotenv import load_dotenv
import os

load_dotenv()
DB_URL = os.getenv("DB_URL")

if not DB_URL:
    raise ValueError('DB_URL is not set in the environment variables.')

engine = create_async_engine(DB_URL, echo=False, pool_size=10, max_overflow=20)
Session = async_sessionmaker(engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(Text, index=True)
    first_name: Mapped[str] = mapped_column(Text)
    last_name: Mapped[str] = mapped_column(Text)
    registered: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    meetings_as_a: Mapped[list['Meeting']] = relationship(back_populates='user_a', cascade='all, delete-orphan', foreign_keys='Meeting.user_a_id')
    meetings_as_b: Mapped[list['Meeting']] = relationship(back_populates='user_b', cascade='all, delete-orphan', foreign_keys='Meeting.user_b_id')

class Meeting(Base):
    __tablename__ = 'meetings'

    __table_args__ = (CheckConstraint('user_a_id <> user_b_id', name='check_diff_users'),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_a_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user_b_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    user_a : Mapped['User'] = relationship(back_populates='meetings_as_a', foreign_keys=[user_a_id])
    user_b : Mapped['User'] = relationship(back_populates='meetings_as_b', foreign_keys=[user_b_id])
    
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)