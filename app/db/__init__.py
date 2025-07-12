from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import get_settings

cfg = get_settings()

engine = create_async_engine(cfg.DB_URL, pool_size=10, max_overflow=20)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    from .models import Base  
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
