import asyncio
import logging

from aiogram import Bot, Dispatcher, Router, types

from app.base import router
from app.database import get_db
from config import TG_BOT_TOKEN

db = get_db()


async def on_startup():
    await db.connect()
    await db.create_tables()
    logging.info('Bot started')


async def on_shutdown():
    await db.close()
    logging.info('Bot stopped')


async def main() -> None:
    dp = Dispatcher()
    dp.include_router(router)
    bot = Bot(TG_BOT_TOKEN, parse_mode="HTML")
    await bot.delete_webhook(drop_pending_updates=True)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    asyncio.run(main())
