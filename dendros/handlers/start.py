from aiogram import Router, F
from aiogram.types import Message
from keyboards.main_kb import main_menu_kb
from services.db import ensure_user, get_user_lang
from services.i18n import t

router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    ensure_user(message.from_user.id, message.from_user.username or "", message.from_user.first_name or "")
    lang = get_user_lang(message.from_user.id)
    text = {
        "kz": "Қош келдіңіз! Басты меню төменде.",
        "ru": "Добро пожаловать! Главное меню ниже.",
        "en": "Welcome! Main menu below."
    }.get(lang, "Добро пожаловать! Главное меню ниже.")
    await message.answer(t(lang, "main_menu_prompt") + "\n\n" + text, reply_markup=main_menu_kb(lang=lang))

# Поддержка текстовой команды открыть меню (альтернативы)
@router.message(F.text == "🏠 Главное меню")
@router.message(F.text == "🏠 Main menu")
@router.message(F.text == "🏠 Басты мәзір")
async def cmd_open_main(message: Message):
    ensure_user(message.from_user.id, message.from_user.username or "", message.from_user.first_name or "")
    lang = get_user_lang(message.from_user.id)
    await message.answer(t(lang, "main_menu_prompt"), reply_markup=main_menu_kb(lang=lang))