from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from services.db import get_lang

router = Router()

FAQ_TEXT_KK = '''❓ *Жиі қойылатын сұрақтар (FAQ)*
• Парктің жұмыс уақыты: 05:00 — 01:00
• Билет: 100 ₸ (кейбір жеңілдіктер бар)
• Адрес: Шымкент, Байдібек би даңғылы, 108/10
'''

FAQ_TEXT_RU = '''❓ *Часто задаваемые вопросы (FAQ)*
• Время работы: 05:00 — 01:00
• Билет: 100 ₸ (есть льготы)
• Адрес: Шымкент, Байдибек би даңғылы, 108/10
'''

@router.message(Command('faq'))
async def cmd_faq(message: Message):
    lang = get_lang(message.from_user.id)
    await message.answer(FAQ_TEXT_RU if lang == 'ru' else FAQ_TEXT_KK, parse_mode='Markdown')
