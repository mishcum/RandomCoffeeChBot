from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User
from app.db.repository import get_user_by_tg


async def is_registered(tg_id: int, db: AsyncSession) -> bool:
    return (await get_user_by_tg(tg_id, db)) is not None


async def create_user(tg_user, first_name: str, last_name: str, db: AsyncSession) -> User:
    user = User(
        tg_id=tg_user.id,
        username=tg_user.username,
        first_name=first_name,
        last_name=last_name,
    )
    db.add(user)
    await db.flush()
    return user