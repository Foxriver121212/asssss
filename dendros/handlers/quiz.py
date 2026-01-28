from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
import json
import os
import logging

from keyboards.main_kb import main_menu_kb
from services.db import (
    ensure_user,
    start_quiz,
    stop_quiz,
    is_quiz_active,
    get_quiz_state,
    advance_quiz,
    get_user_lang
)
from services.i18n import t

router = Router()
logging.getLogger().setLevel(logging.INFO)

QUIZ_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "quiz_data.json")

def _load_quiz():
    try:
        with open(QUIZ_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                logging.error("Quiz file must contain a list of questions")
                return []
            return data
    except Exception as e:
        logging.exception("Failed to load quiz file: %s", e)
        return []

QUIZ = _load_quiz()
logging.info("Loaded quiz with %d questions", len(QUIZ))

EXIT_BTN = "❌ Выйти"
START_TEXTS = {"ru": "🧪 Викторина", "kz": "🧪 Викторина", "en": "🧪 Quiz"}

def build_answers_kb(opts):
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[[KeyboardButton(text=o)] for o in opts] + [[KeyboardButton(text=EXIT_BTN)]]
    )

@router.message(F.text.in_({START_TEXTS["ru"], START_TEXTS["en"], START_TEXTS["kz"]}))
async def cmd_quiz_start(message: Message):
    ensure_user(message.from_user.id, message.from_user.username or message.from_user.first_name)
    # Перезагружаем вопросы на случай правок файла
    global QUIZ
    QUIZ = _load_quiz()
    logging.info("User %s started quiz; questions=%d", message.from_user.id, len(QUIZ))
    lang = get_user_lang(message.from_user.id)
    if not QUIZ:
        await message.answer(t(lang, "quiz_start") + "\n\n" + "Викторина временно недоступна.", reply_markup=main_menu_kb(lang=lang))
        return
    start_quiz(message.from_user.id)
    await send_current_question(message)

async def send_current_question(message: Message):
    state = get_quiz_state(message.from_user.id)
    progress = state.get("progress", 0)
    score = state.get("score", 0)
    lang = get_user_lang(message.from_user.id)

    if progress >= len(QUIZ):
        await message.answer(t(lang, "quiz_finished", score=score, total=len(QUIZ)), reply_markup=main_menu_kb(lang=lang))
        stop_quiz(message.from_user.id)
        return

    q = QUIZ[progress]
    q_text_block = q.get("q", {})
    opts_block = q.get("opts", {})
    q_text_str = q_text_block.get(lang) or q_text_block.get("ru") or str(q_text_block)
    opts = opts_block.get(lang) or opts_block.get("ru") or []

    if not isinstance(opts, list):
        opts = list(opts)

    text = f"❓ {q_text_str}\n\n"
    for i, o in enumerate(opts, 1):
        text += f"{i}) {o}\n"

    await message.answer(text, reply_markup=build_answers_kb(opts))

@router.message(F.text == EXIT_BTN)
async def quiz_exit_button(message: Message):
    stop_quiz(message.from_user.id)
    lang = get_user_lang(message.from_user.id)
    await message.answer(t(lang, "quiz_exit_confirm"), reply_markup=main_menu_kb(lang=lang))

def normalize(s: str):
    return (s or "").strip().lower().replace(".", "").replace("  ", " ")

@router.message(lambda message: is_quiz_active(message.from_user.id))
async def quiz_answer_handler(message: Message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    text = normalize(message.text)

    # Allow textual exit variants too
    if text in ("stop", "выйти", "стоп", "exit"):
        stop_quiz(user_id)
        await message.answer(t(lang, "quiz_exit_confirm"), reply_markup=main_menu_kb(lang=lang))
        return

    state = get_quiz_state(user_id)
    progress = state.get("progress", 0)

    if progress >= len(QUIZ):
        stop_quiz(user_id)
        await message.answer(t(lang, "quiz_finished", score=state.get("score", 0), total=len(QUIZ)), reply_markup=main_menu_kb(lang=lang))
        return

    q = QUIZ[progress]
    opts = q.get("opts", {}).get(lang) or q.get("opts", {}).get("ru") or []
    answer_correct = q.get("a", {}).get(lang) or q.get("a", {}).get("ru")
    explanation = q.get("explanation", {}).get(lang) if isinstance(q.get("explanation"), dict) else q.get("explanation", "")

    selected = None
    # choose by number
    if text.isdigit():
        idx = int(text) - 1
        if 0 <= idx < len(opts):
            selected = opts[idx]

    # choose by text
    if selected is None:
        for o in opts:
            if normalize(o) == text:
                selected = o
                break

    if selected is None:
        await message.answer(t(lang, "pick_from_buttons"), reply_markup=build_answers_kb(opts))
        return

    correct = False
    if answer_correct is not None:
        correct = normalize(selected) == normalize(answer_correct)

    advance_quiz(user_id, correct=correct)

    # Сообщаем результат, затем отправляем следующий вопрос (если есть)
    if correct:
        await message.answer(t(lang, "answer_correct"), reply_markup=build_answers_kb(opts))
    else:
        await message.answer(t(lang, "answer_wrong", answer=answer_correct or "", ex=explanation or ""), reply_markup=build_answers_kb(opts))

    # Отправляем следующий вопрос (или финальное сообщение)
    await send_current_question(message)