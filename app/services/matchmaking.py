import random
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User, Meeting
from app.db.enums import MeetingStatus, Office


async def find_partner(me: User, db: AsyncSession) -> User | None:
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

    blocked = blocked_a.union_all(blocked_b)

    candidates = select(User).where(User.id != me.id, ~User.id.in_(blocked))

    if me.office != Office.all_:
        candidates = candidates.where(User.office == me.office)

    candidates = (await db.scalars(candidates)).all()

    return random.choice(candidates) if candidates else None
