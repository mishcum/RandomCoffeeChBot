from dotenv import load_dotenv
import os
import asyncio
import logging
import random

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.bd import init_db, Session, User, Meeting, MeetingStatus, reset_meetings
from sqlalchemy import select, or_, and_
from app.keyboards import reg_button, main_buttons, meet_candidate_kb, answer_request_kb
from sqlalchemy.sql import func

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s %(name)s | %(message)s")

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError('BOT_TOKEN is not set in the environment variables.')

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

class Reg(StatesGroup):
    waiting_registration = State()

@dp.message(F.text == 'Профиль')
async def profile(message: Message) -> None:
    async with Session() as session:
        user = await session.scalar(select(User).where(User.tg_id == message.from_user.id))
    
    if user:
        await message.answer(text=f'Твой профиль:\n\n*Имя:* {user.first_name}\n*Фамилия:* {user.last_name}\n*Пользовательское имя:* @{user.username or "—"}\n*ID в Telegram:* {user.tg_id}', parse_mode='Markdown', reply_markup=main_buttons)
    else:
        await message.answer(text='Ты не зарегестрирован! Напиши /start, чтобы начать.', reply_markup=reg_button)

@dp.message(CommandStart())
async def start_command(message: Message, state: FSMContext) -> None:
    await state.clear()

    async with Session() as session:
        user = await session.scalar(select(User).where(User.tg_id == message.from_user.id))

    if user:
        await message.answer(text=f'С возвращением, *{message.from_user.full_name}*!👋\nХочешь встретиться с кем-нибудь?.', parse_mode='Markdown', reply_markup=main_buttons)
    else:
        await message.answer(text=f'Привет, *{message.from_user.full_name}*!👋\nЯ бот для случайных встреч. Зарегестрируйся, чтобы начать! ☕️', parse_mode='Markdown', reply_markup=reg_button)

@dp.message(F.text == 'Регистрация 🚀')
async def registration(message: Message, state : FSMContext) -> None:
    async with Session() as session:
        is_exists = await session.scalar(select(User).where(User.tg_id == message.from_user.id))
        if is_exists:
            await message.answer(text='Ты уже зарегестрирван!✅\nНапиши /meet, чтобы начать.', parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
            return
        else:
            await message.answer(text='Давай знакомиться! 😀\nНапиши свои *имя и фамилию* одним сообщением, например: `Лена Головач`', parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
            await state.set_state(Reg.waiting_registration)

@dp.message(Reg.waiting_registration, F.text)
async def save_name(message : Message, state : FSMContext) -> None: 
    splitted = message.text.strip().split()
    if len(splitted) != 2:
        await message.answer(text='Пожалуйста, введи *имя и фамилию* одним сообщением, например: `Лена Головач`', parse_mode='Markdown')
        return
    
    fname, lname = splitted
    async with Session.begin() as session:
        user = await session.scalar(select(User).where(User.tg_id == message.from_user.id).with_for_update())
        if user:
            await message.answer(text='Ты уже зарегестрирван!✅\nНапиши /meet, чтобы начать.', parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
            await state.clear()
            return
        
        session.add(User(
            tg_id=message.from_user.id,
            username=message.from_user.username,
            first_name=fname,
            last_name=lname
        ))

        await message.answer(f'Спасибо, *{fname}*! Ты c нами ✅\n Нажми «Встретиться ☕️», чтобы найти собеседника.', reply_markup=main_buttons, parse_mode='Markdown')
        await state.clear()

async def _available_persons(sess, me_id: int):
    blocked = select(Meeting.user_b_id).where(
        or_(
            and_(Meeting.user_a_id == me_id,
                 Meeting.status.in_([MeetingStatus.pending,
                                     MeetingStatus.confirmed])),
            and_(Meeting.user_b_id == me_id,
                 Meeting.status.in_([MeetingStatus.pending,
                                     MeetingStatus.confirmed]))
        )
    )
    return (await sess.scalars(select(User).where(User.id != me_id, ~User.id.in_(blocked)))).all()

@dp.message(F.text == 'Встретиться ☕️')
async def find_person(message : Message) -> None:
    async with Session() as session:
        me: User = await session.scalar(select(User).where(User.tg_id == message.from_user.id))
        candidates = await _available_persons(session, me.id)

    if not candidates:
        await reset_meetings(me.id, session)
        await session.commit()         
        candidates = await _available_persons(session, me.id)
    
    if not candidates:
        await message.answer('Нет свободных собеседников, попробуй позже ☕️')
        return

    person = random.choice(candidates)
    await message.answer(f'Как насчёт встречи с *{person.first_name} {person.last_name}*?', parse_mode="Markdown", reply_markup=meet_candidate_kb(person.tg_id))

@dp.callback_query(F.data == 'meet_other')
async def meet_other(callback: CallbackQuery):
    await callback.message.delete()
    await find_person(callback.message)

@dp.callback_query(F.data.startswith('meet_request:'))
async def meet_request(callback: CallbackQuery):
    initiator_tg = callback.from_user.id
    person_tg = int(callback.data.split(':')[1])

    async with Session.begin() as session:
        initiator = await session.scalar(select(User).where(User.tg_id == initiator_tg))
        person = await session.scalar(select(User).where(User.tg_id == person_tg))

        stmt = select(Meeting).where(
            or_(
                and_(Meeting.user_a_id == initiator.id, Meeting.user_b_id == person.id),
                and_(Meeting.user_a_id == person.id, Meeting.user_b_id == initiator.id)
            )
        )
        meet: Meeting | None = await session.scalar(stmt)
        if meet and meet.status == MeetingStatus.pending:
            await callback.answer("Запрос уже отправлен 💌", show_alert=True)
            return
        if meet and meet.status in {MeetingStatus.declined, MeetingStatus.archived}:
            meet.status = MeetingStatus.pending
            meet.user_a_id, meet.user_b_id = initiator.id, person.id
            meet.created_at = func.now()
        if not meet:
            meet = Meeting(user_a_id=initiator.id, user_b_id=person.id, status=MeetingStatus.pending)
            session.add(meet)
        await session.flush() 

    await callback.message.edit_text(f'Запрос отправлен *{person.first_name}* ✅\nОжидаем ответ…', reply_markup=None, parse_mode='Markdown')

    await bot.send_message(person_tg, f'*{initiator.first_name} {initiator.last_name}* хочет встретиться с вами. 😀', parse_mode='Markdown', reply_markup=answer_request_kb(meet.id))

@dp.callback_query(F.data.startswith(("meet_accept:", "meet_decline:")))
async def meet_response(callback: CallbackQuery):
    action, meet_id_txt = callback.data.split(":")
    meet_id = int(meet_id_txt)

    async with Session.begin() as session:
        stmt = (
            select(Meeting)
            .where(Meeting.id == meet_id)
            .with_for_update()
        )
        meet: Meeting | None = await session.scalar(stmt)

        if not meet or meet.status != MeetingStatus.pending:
            await callback.answer("Заявка уже обработана", show_alert=True)
            return

        initiator = await session.get(User, meet.user_a_id)
        partner   = await session.get(User, meet.user_b_id)

        if action == "meet_accept":
            meet.status = MeetingStatus.confirmed
            await session.flush()     

            await bot.send_message(
                initiator.tg_id,
                f"🎉 *{partner.first_name}* согласился!\n"
                f"Свяжитесь в Telegram:\n"
                f"• @{initiator.username or '—'}\n"
                f"• @{partner.username   or '—'}",
                parse_mode="Markdown",
            )
            await callback.message.edit_text(
                "Вы подтвердили встречу!\n"
                "Данные собеседника отправлены обеим сторонам.",
                reply_markup=None,
            )
        else:
            meet.status = MeetingStatus.declined
            await session.flush()

            await bot.send_message(
                initiator.tg_id,
                f"😔 *{partner.first_name}* отказался от встречи.\n"
                "Попробуйте выбрать другого собеседника.",
            )
            await callback.message.edit_text(
                "Вы отклонили запрос.\n"
                "Можно нажать «Встретиться» и выбрать нового человека.",
                reply_markup=None,
            )

@dp.message(F.text)
async def fallback(message: Message):
    await message.answer("Набери /start или нажми «Регистрация» 🙂")

async def main() -> None:
    await init_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())