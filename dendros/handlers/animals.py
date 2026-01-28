from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import json, pathlib
router = Router()
DATA_FILE = pathlib.Path(__file__).parent.parent / 'data' / 'animals.json'
def load():
    try:
        return json.loads(DATA_FILE.read_text(encoding='utf-8'))
    except:
        return []
@router.message(Command('animals'))
async def cmd_animals(message: Message):
    animals = load()
    if not animals:
        await message.answer('Animals list is empty.')
        return
    text = 'Animals in park:\n'
    for a in animals[:20]:
        text += f"\n• {a['name']} — {a.get('desc','')}\n"
    await message.answer(text)
