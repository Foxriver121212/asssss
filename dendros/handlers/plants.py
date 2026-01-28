from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import json, pathlib
router = Router()
DATA_FILE = pathlib.Path(__file__).parent.parent / 'data' / 'plants.json'
def load():
    try:
        return json.loads(DATA_FILE.read_text(encoding='utf-8'))
    except:
        return []
@router.message(Command('plants'))
async def cmd_plants(message: Message):
    plants = load()
    if not plants:
        await message.answer('Растения отсутствуют.')
        return
    text = 'Растения парка:\n'
    for p in plants[:20]:
        text += f"\n• {p['name']} — {p.get('latin','')}: {p.get('desc','')}\n"
    await message.answer(text)
