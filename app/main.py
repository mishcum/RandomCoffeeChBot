from aiogram import Bot, Dispatcher
from app.config import get_settings
from app.handlers.init import register_all
from app.db import init_db
import asyncio, logging

async def main():
    cfg = get_settings()
    logging.basicConfig(level=cfg.LOG_LEVEL)
    await init_db()

    bot = Bot(cfg.BOT_TOKEN)
    dp  = Dispatcher()
    register_all(dp)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
