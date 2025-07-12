from sqlalchemy import select, update, or_
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User, Meeting
from .enums import MeetingStatus

async def get_user_by_tg(tg_id: int, db: AsyncSession) -> User | None:
    return await db.scalar(select(User).where(User.tg_id == tg_id))

async def reset_meetings(user_id: int, db: AsyncSession) -> None:
    await db.execute(
        update(Meeting)
        .where(or_(Meeting.user_a_id == user_id,
                   Meeting.user_b_id == user_id),
               Meeting.status.in_([MeetingStatus.pending,
                                   MeetingStatus.confirmed,
                                   MeetingStatus.declined]))
        .values(status=MeetingStatus.archived))
