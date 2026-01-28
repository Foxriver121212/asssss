from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
router = Router()
@router.message(Command('achievements'))
async def cmd_ach(message: Message):
    await message.answer('Достижения: Пока что пусто — будет добавлено позже.')
