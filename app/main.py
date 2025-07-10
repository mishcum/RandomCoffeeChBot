from dotenv import load_dotenv
import os
import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError('BOT_TOKEN is not set in the environment variables.')


bot = Bot(BOT_TOKEN)
dp = Dispatcher()

regbutton = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Регистрация 🚀')]],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def start_command(message: Message) -> None:
    await message.answer(text=f'Привет, *{message.from_user.full_name}*!👋\nЯ бот для случайных встреч. Напиши /meet, чтобы начать.', parse_mode='Markdown')

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())