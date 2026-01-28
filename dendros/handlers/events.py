from aiogram import Router, F
from aiogram.types import Message
from services.db import ensure_user, get_lang, get_events
from keyboards.main_kb import main_menu_kb

router = Router()


@router.message(F.text == "📅 Іс-шаралар")
async def cmd_events(message: Message):
    ensure_user(message.from_user.id, message.from_user.first_name)
    lang = get_lang(message.from_user.id)

    events = get_events()

    if not events:
        await message.answer(
            "📅 Қазіргі уақытта ешқандай іс-шара жоқ.",
            reply_markup=main_menu_kb()
        )
        return

    text = "📅 *Алдағы іс-шаралар:*\n\n"
    for ev in events:
        text += f"🔹 *{ev.get('title', 'Атауы жоқ')}*\n"
        text += f"📆 {ev.get('date', 'Күні көрсетілмеген')}\n"
        text += f"📍 {ev.get('location', 'Орны көрсетілмеген')}\n"
        desc = ev.get('description')
        if desc:
            text += f"📝 {desc}\n"
        text += "\n"

    await message.answer(text, parse_mode="Markdown", reply_markup=main_menu_kb())
