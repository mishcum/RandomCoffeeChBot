from aiogram import Router, F
from aiogram.types import Message
from app.db import SessionLocal
from app.services.stats import get_global_stats
from app.keyboards.reply import main_buttons

router = Router()

@router.message(F.text == 'Инфо ℹ️')
async def bot_info(msg : Message):
    async with SessionLocal() as db:
        users_count, meetengs_count = await get_global_stats(db)
    
    await msg.answer(
        "Привет! 👋 Это RandomCoffeeBot ☕️! Я помогу организовать встречу с твоим коллегой.\n"
        "Я - прототип настоящего решения - мои создатели участвуют в кейс-чемпионате от Газпром Банка.\n\n"
        f"Всего зарегистрировано пользователей: {users_count}\n"
        f"Всего встречено: {meetengs_count}\n\n"
        "Нажми «Встретиться ☕️», чтобы найти собеседника.",
        parse_mode='Markdown',
        reply_markup=main_buttons
    )