from aiogram import Router, F
from aiogram.types import Message
from services.db import ensure_user, get_lang, get_leaderboard
from keyboards.main_kb import main_menu_kb

router = Router()


@router.message(F.text == "🏆 Лидерборд")
async def cmd_leaderboard(message: Message):
    ensure_user(message.from_user.id, message.from_user.first_name)
    lang = get_lang(message.from_user.id)

    leaders = get_leaderboard()

    if not leaders:
        await message.answer(
            "🏆 Лидерборд бос.",
            reply_markup=main_menu_kb()
        )
        return

    text = "🏆 *Үздік қатысушылар:*\n\n"

    for i, user in enumerate(leaders, start=1):
        name = user.get("name", "Аты жоқ")
        score = user.get("correct_answers", 0)
        text += f"{i}. *{name}* — {score} дұрыс жауап\n"

    await message.answer(text, parse_mode="Markdown", reply_markup=main_menu_kb())
