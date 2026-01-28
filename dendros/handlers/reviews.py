from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
router = Router()
@router.message(Command('reviews'))
async def cmd_reviews(message: Message):
    await message.answer('Отзывы: пока пусто. Оставьте отзыв через /feedback (планируется).')
