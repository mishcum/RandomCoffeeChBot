from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.keyboards.reply import main_buttons
from app.db import SessionLocal
from app.db.repository import get_user_by_tg
from app.services.registration import create_user

router = Router()


class Reg(StatesGroup):
    waiting_name = State()


@router.message(F.text == 'Регистрация 🚀')
async def ask_name(msg: Message, state: FSMContext):
    async with SessionLocal() as db:
        if await get_user_by_tg(msg.from_user.id, db):
            await msg.answer('Ты уже зарегистрирован ✅', reply_markup=ReplyKeyboardRemove())
            return

    await msg.answer(
        'Давай знакомиться! 😀\nНапиши *имя и фамилию* одним сообщением, например: `Лена Головач`', parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
    await state.set_state(Reg.waiting_name)


@router.message(Reg.waiting_name, F.text)
async def save_name(msg: Message, state: FSMContext):
    parts = msg.text.split(maxsplit=1)
    if len(parts) != 2:
        await msg.answer('Пожалуйста, два слова: имя и фамилия 🙂')
        return

    first, last = parts
    async with SessionLocal.begin() as db:
        await create_user(msg.from_user, first, last, db)

    await msg.answer(
        f'Спасибо, *{first}*! Ты с нами ✅\nНажми «Встретиться ☕️», чтобы найти собеседника.', parse_mode='Markdown', reply_markup=main_buttons)
    await state.clear()
