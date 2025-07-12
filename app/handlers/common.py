from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from app.keyboards.reply import reg_button, main_buttons
from app.db import SessionLocal
from app.db.repository import get_user_by_tg

router = Router()

@router.message(CommandStart())
async def cmd_start(msg: Message, state):
    await state.clear()

    async with SessionLocal() as db:
        user = await get_user_by_tg(msg.from_user.id, db)

    if user:
        await msg.answer(
            f'С возвращением, *{msg.from_user.full_name}*! 👋\n'
            'Нажми «Встретиться ☕️», чтобы найти собеседника.',
            parse_mode='Markdown',
            reply_markup=main_buttons,
        )
    else:
        await msg.answer(
            f'Привет, *{msg.from_user.full_name}*! 👋\n'
            'Я бот для случайных встреч. Мои создатели участвуют в кейс-чемпионате от Газпром Банка.\nЗарегистрируйся, чтобы начать! ☕️',
            parse_mode='Markdown',
            reply_markup=reg_button,
        )


@router.message(F.text, flags={'allow_processing_to_continue': True})
async def fallback(msg: Message):
    await msg.answer('Набери /start или нажми «Регистрация 🚀» 🙂')
