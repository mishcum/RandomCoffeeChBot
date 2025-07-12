import random
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User, Meeting
from app.db.enums import MeetingStatus


async def find_partner(me: User, db: AsyncSession) -> User | None:
    # 1. два запроса на user_a_id и user_b_id
    blocked_a = (
        select(Meeting.user_b_id)
        .where(Meeting.user_a_id == me.id,
               Meeting.status.in_([MeetingStatus.pending,
                                   MeetingStatus.confirmed]))
    )
    blocked_b = (
        select(Meeting.user_a_id)
        .where(Meeting.user_b_id == me.id,
               Meeting.status.in_([MeetingStatus.pending,
                                   MeetingStatus.confirmed]))
    )

    # 2. объединяем в один подзапрос
    blocked = blocked_a.union_all(blocked_b)

    # 3. ищем всех, кто не в blocked
    candidates = (await db.scalars(
        select(User).where(
            User.id != me.id,
            ~User.id.in_(blocked)          # исключаем обе стороны
        )
    )).all()

    return random.choice(candidates) if candidates else None
