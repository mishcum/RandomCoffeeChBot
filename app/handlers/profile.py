from aiogram import Router, F
from aiogram.types import Message
from app.keyboards.reply import reg_button, main_buttons
from app.db import SessionLocal
from app.db.repository import get_user_by_tg
from app.services.profile import build_profile_text

router = Router()


@router.message(F.text == 'Профиль')
async def profile(msg: Message):
    async with SessionLocal() as db:
        user = await get_user_by_tg(msg.from_user.id, db)

    if not user:
        await msg.answer('Ты не зарегистрирован! Нажми /start.', reply_markup=reg_button)
        return

    await msg.answer(build_profile_text(user), parse_mode='Markdown', reply_markup=main_buttons)
