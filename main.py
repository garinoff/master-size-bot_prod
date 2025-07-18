import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from database.database import init_db
from handlers import (
    start, profile, tasks, referral, 
    size_guru, wallet, admin
)
from middleware.auth import AuthMiddleware

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    # Инициализация бота и диспетчера
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    
    dp = Dispatcher(storage=MemoryStorage())
    
    # Middleware
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    
    # Инициализация базы данных
    await init_db()
    
    # Регистрация handlers
    dp.include_routers(
        start.router,
        profile.router,
        tasks.router,
        referral.router,
        size_guru.router,
        wallet.router,
        admin.router
    )
    
    logger.info("🚀 Мастер-размер бот запущен!")
    
    # Запуск polling
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
