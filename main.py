import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import API_TOKEN, DATABASE_URL
from db import init_db_pool
from handlers.start import router as start_router
from handlers.setkey import router as setkey_router
from handlers.top_day import router as top_router
from handlers.top_week import router as week_router

logging.basicConfig(level=logging.INFO)


async def main():
    await init_db_pool(DATABASE_URL)
    bot = Bot(API_TOKEN, parse_mode="HTML")
    
    # Удаляем вебхук перед запуском в режиме polling
    await bot.delete_webhook()
    
    # Используем MemoryStorage для хранения состояний FSM
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Включаем роутеры
    dp.include_router(start_router)
    dp.include_router(setkey_router)
    dp.include_router(top_router)
    dp.include_router(week_router)

    try:
        logging.info("Бот запущен. Ожидаем сообщений...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
