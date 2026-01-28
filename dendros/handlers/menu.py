from aiogram import Router, F
from aiogram.types import Message
from keyboards.main_kb import main_menu_kb
from services.i18n import t
from services.messenger import send_text
from services.db import ensure_user, get_user_lang

router = Router()

@router.message(F.text == "/start")
async def menu_start(message: Message):
    """
    Начальное сообщение: сохраняет пользователя и показывает главное меню.
    Использует безопасную отправку через send_text.
    """
    ensure_user(message.from_user.id, message.from_user.username or "", message.from_user.first_name or "")
    lang = get_user_lang(message.from_user.id) or "ru"
    await send_text(message, t(lang, "main_menu_prompt"), reply_markup=main_menu_kb(lang=lang))

@router.message(F.text == "🌐 Тіл")
@router.message(F.text == "🌐 Language")
@router.message(F.text == "🌐 Язык")
async def menu_lang(message: Message):
    """
    Показать экран выбора языка.
    Делегирует отправку безопасному helper'у cmd_lang_start из handlers/lang.py
    """
    # Импорт локально, чтобы избежать циклических импортов
    from handlers.lang import cmd_lang_start
    await cmd_lang_start(message)