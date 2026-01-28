from aiogram import Router, F
from aiogram.types import Message
from services.db import ensure_user, get_user_lang
from services.i18n import t
from keyboards.main_kb import main_menu_kb

router = Router()

@router.message(F.text.in_({"👤 Профиль", "👤 Profile", "👤 Профиль"}))
async def cmd_profile(message: Message):
    user = message.from_user
    lang = get_user_lang(user.id) or "ru"

    # Сохраняем пользователя в БД, если нужно
    ensure_user(user.id, user.username or "", user.first_name or "")

    # Формируем имя
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    username = f"@{user.username}" if user.username else "—"

    # Ответ
    text = {
        "ru": f"👤 Ваш профиль:\n\nИмя: {full_name or 'Аноним'}\nЮзернейм: {username}",
        "kz": f"👤 Пайдаланушы :\n\nАты: {full_name or 'Аноним'}\nПайдаланушы аты: {username}",
        "en": f"👤 Your profile:\n\nName: {full_name or 'Anonymous'}\nUsername: {username}"
    }.get(lang, f"👤 Имя: {full_name or 'Аноним'}\nЮзернейм: {username}")

    await message.answer(text, reply_markup=main_menu_kb(lang=lang))