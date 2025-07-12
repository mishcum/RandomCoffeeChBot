from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, User as TgUser
from app.keyboards.inline import meet_candidate_kb
from app.db import SessionLocal
from app.db.repository import get_user_by_tg, reset_meetings
from app.services.matchmaking import find_partner

router = Router()

async def _start_matchmaking(tg_user: TgUser, sender_msg: Message):
    async with SessionLocal.begin() as db:
        me = await get_user_by_tg(tg_user.id, db)
        if not me:
            await sender_msg.answer('Сначала зарегистрируйтесь через /start')
            return

        partner = await find_partner(me, db)
        if partner is None:
            await reset_meetings(me.id, db)
            await db.flush()
            partner = await find_partner(me, db)

    if partner is None:
        await sender_msg.answer('Нет свободных собеседников, попробуй позже ☕️')
        return

    await sender_msg.answer(
        f'Как насчёт встречи с *{partner.first_name} {partner.last_name}*?', parse_mode='Markdown', reply_markup=meet_candidate_kb(partner.tg_id))

@router.message(F.text == 'Встретиться ☕️')
async def meet_command(msg: Message):
    await _start_matchmaking(msg.from_user, msg)

@router.callback_query(F.data == 'meet_other')
async def meet_other(cb: CallbackQuery):
    await cb.message.delete()
    await _start_matchmaking(tg_user=cb.from_user, sender_msg=cb.message)
