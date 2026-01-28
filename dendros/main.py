import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from keep_alive import keep_alive
keep_alive()


# Импорт роутеров
from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.info import router as info_router
from handlers.faq import router as faq_router
from handlers.profile import router as profile_router
from handlers.quiz import router as quiz_router
from handlers.lang import router as lang_router

# Загружаем токен из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("❌ ERROR: BOT_TOKEN not found in .env")
    exit(1)

# Логирование
logging.basicConfig(level=logging.INFO)

# Создание бота с правильным способом передачи parse_mode
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# Подключение роутеров
dp.include_router(start_router)
dp.include_router(menu_router)
dp.include_router(info_router)
dp.include_router(faq_router)
dp.include_router(profile_router)
dp.include_router(quiz_router)
dp.include_router(lang_router)

# Запуск
async def main():
    print("🚀 Бот успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())