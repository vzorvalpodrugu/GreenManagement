import asyncio
import os
from aiogram import Bot, Dispatcher
import dotenv
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import handlers
from database import db

load_dotenv()
BOT_API_KEY = os.getenv('TG_API_KEY')

async def main():
    bot = Bot(token=BOT_API_KEY)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(handlers.router)

    await db.create_pool()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


