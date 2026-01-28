from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
router = Router()
@router.message(Command('search'))
async def cmd_search(message: Message):
    await message.answer('Поиск пока недоступен. Скоро будет.')
