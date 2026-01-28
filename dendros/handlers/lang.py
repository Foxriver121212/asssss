# handlers/lang.py
from aiogram import Router, F
from aiogram.types import Message
from keyboards.main_kb import lang_kb, main_menu_kb
from services.i18n import t
from services.messenger import send_text
from services.db import ensure_user, set_user_lang

router = Router()

@router.message(F.text.in_({"🇰🇿 Қазақша", "🇷🇺 Русский", "🇬🇧 English"}))
async def choose_language(message: Message):
    """
    User pressed a language button from lang_kb.
    Save language and show main menu.
    """
    mapping = {
        "🇰🇿 Қазақша": "kz",
        "🇷🇺 Русский": "ru",
        "🇬🇧 English": "en"
    }
    lang = mapping.get(message.text, "ru")
    ensure_user(message.from_user.id, message.from_user.username or "", message.from_user.first_name or "")
    set_user_lang(message.from_user.id, lang)
    # Greet user and show main menu
    await send_text(message, t(lang, "main_menu_prompt"), reply_markup=main_menu_kb(lang=lang))

async def cmd_lang_start(message: Message):
    """
    Send language selection keyboard (used from other handlers).
    Use safe send_text to avoid empty-text error.
    """
    await send_text(message, t("ru", "choose_language"), reply_markup=lang_kb())