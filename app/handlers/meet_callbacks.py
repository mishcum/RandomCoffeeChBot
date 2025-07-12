from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import and_, or_, select
from sqlalchemy.sql import func

from app.keyboards.inline import answer_request_kb
from app.db import SessionLocal
from app.db.models import User, Meeting
from app.db.enums import MeetingStatus
from app.db.repository import get_user_by_tg
from app.services.matchmaking import find_partner
from app.keyboards.inline import meet_candidate_kb, answer_request_kb


router = Router()


@router.callback_query(F.data.startswith('meet_request:'))
async def meet_request(cb: CallbackQuery):
    initiator_tg = cb.from_user.id
    partner_tg = int(cb.data.split(':')[1])

    async with SessionLocal.begin() as db:
        ini = await get_user_by_tg(initiator_tg, db)
        par = await get_user_by_tg(partner_tg, db)

        stmt = select(Meeting).where(
            or_(
                and_(Meeting.user_a_id == ini.id, Meeting.user_b_id == par.id),
                and_(Meeting.user_a_id == par.id, Meeting.user_b_id == ini.id),
            )
        )
        meet: Meeting | None = await db.scalar(stmt)

        if meet and meet.status == MeetingStatus.pending:
            await cb.answer('Запрос уже отправлен 💌', show_alert=True)
            return

        if meet and meet.status in {MeetingStatus.declined, MeetingStatus.archived}:
            meet.status = MeetingStatus.pending
            meet.user_a_id, meet.user_b_id = ini.id, par.id
            meet.created_at = func.now()
        if not meet:
            meet = Meeting(user_a_id=ini.id, user_b_id=par.id, status=MeetingStatus.pending)
            db.add(meet)
        await db.flush()  

    await cb.message.edit_text(f'Запрос отправлен *{par.first_name}* ✅\nОжидаем ответ…', parse_mode='Markdown')
    await cb.bot.send_message(partner_tg, f'*{ini.first_name} {ini.last_name}* хочет встретиться с вами 😃', parse_mode='Markdown', reply_markup=answer_request_kb(meet.id))


@router.callback_query(F.data.startswith(('meet_accept:', 'meet_decline:')))
async def meet_response(cb: CallbackQuery):
    action, meet_id_s = cb.data.split(':')
    meet_id = int(meet_id_s)

    async with SessionLocal.begin() as db:
        meet: Meeting | None = await db.get(Meeting, meet_id, with_for_update=True)
        if not meet or meet.status != MeetingStatus.pending:
            await cb.answer('Заявка уже обработана', show_alert=True)
            return

        initiator = await db.get(User, meet.user_a_id)
        partner = await db.get(User, meet.user_b_id)

        contacts_text = (
            f'🎉 Встреча подтверждена!\n'
            f'Свяжитесь друг с другом:\n'
            f'• @{initiator.username or '—'} – {initiator.first_name}\n'
            f'• @{partner.username or '—'} – {partner.first_name}'
        )

        if action == 'meet_accept':
            meet.status = MeetingStatus.confirmed
            await db.flush()

            await cb.bot.send_message(initiator.tg_id, contacts_text, parse_mode='Markdown')
            await cb.bot.send_message(partner.tg_id, contacts_text, parse_mode='Markdown')

            await cb.message.edit_text('Вы подтвердили встречу! Контакты отправлены обеим сторонам.')
        else:
            meet.status = MeetingStatus.declined
            await db.flush()

            await cb.bot.send_message(initiator.tg_id, f'😔 *{partner.first_name}* отказался от встречи.\nПопробуйте выбрать другого собеседника.', parse_mode='Markdown')
            
            await cb.message.edit_text('Вы отклонили запрос. Нажмите «Встретиться» и выберите нового человека.')

