from dotenv import load_dotenv
import os
import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.bd import init_db, Session, User, Meeting
from sqlalchemy import select

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s %(name)s | %(message)s")

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError('BOT_TOKEN is not set in the environment variables.')

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

class Reg(StatesGroup):
    waiting_registration = State()

regbutton = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Регистрация 🚀')]],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def start_command(message: Message, state: FSMContext) -> None:
    await state.clear()

    async with Session() as session:
        user = await session.scalar(select(User).where(User.tg_id == message.from_user.id))

    if user:
        await message.answer(text=f'С возвращением, *{message.from_user.full_name}*!👋\nНапиши /meet, чтобы начать.', parse_mode='Markdown')
    else:
        await message.answer(text=f'Привет, *{message.from_user.full_name}*!👋\nЯ бот для случайных встреч. Зарегестрируйся, чтобы начать! ☕️', parse_mode='Markdown', reply_markup=regbutton)

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

        await message.answer(f"Спасибо, *{fname}*! Ты c нами ✅", reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown')
        await state.clear()

@dp.message(F.text)
async def fallback(msg: Message):
    await msg.answer("Набери /start или нажми «Регистрация» 🙂")

async def main() -> None:
    await init_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())