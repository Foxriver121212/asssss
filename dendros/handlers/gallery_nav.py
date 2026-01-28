from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from pathlib import Path
router = Router()
BASE = Path(__file__).parent.parent
IMG_DIR = BASE / 'images'
@router.message(Command('gallery_next'))
async def gallery_next(message: Message):
    imgs = sorted([p for p in IMG_DIR.iterdir() if p.suffix.lower() in ('.jpg','.png')]) if IMG_DIR.exists() else []
    if not imgs:
        await message.answer('No images')
        return
    await message.answer_photo(photo=imgs[0].open('rb'))
