from aiogram import Router, F
from aiogram.types import Message

from services.db import list_users, add_event, get_events

router = Router()

ADMIN_ID = 000000000  # ← обязательно замени на свой Telegram ID !!!

@router.message(F.text == "👑 Админ-панель")
async def admin_menu(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ У вас нет доступа.")

    text = (
        "👑 *Админ-панель*\n"
        "Выберите действие:\n\n"
        "📢 Добавить объявление\n"
        "👥 Список пользователей"
    )

    await message.answer(text)

# ---------- Добавление объявления ----------

@router.message(F.text == "📢 Добавить объявление")
async def ask_event(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer("Введите текст объявления:")
    message.conf.set("event_mode", True)

@router.message()
async def save_event(message: Message):
    if message.conf.get("event_mode"):
        add_event(message.text)
        message.conf["event_mode"] = False
        await message.answer("✅ Объявление добавлено!")

# ---------- Список пользователей ----------

@router.message(F.text == "👥 Список пользователей")
async def admin_users(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    users = list_users()

    if not users:
        return await message.answer("Список пуст.")

    text = "👥 *Список пользователей:*\n\n"
    for uid, data in users.items():
        text += f"• {uid} — {data.get('name', 'Unknown')}\n"

    await message.answer(text)
