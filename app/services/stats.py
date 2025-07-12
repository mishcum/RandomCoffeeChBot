from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models import User

async def get_global_stats(db : AsyncSession) -> tuple[int, int]:
    users_count = await db.scalar(select(func.count()).select_from(User))
    meetengs_count = await db.scalar(select(func.coalesce(func.sum(User.meetings_count), 0)))
    return users_count or 0, meetengs_count // 2 or 0