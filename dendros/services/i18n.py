# services/i18n.py
from typing import Dict
import logging

STRINGS: Dict[str, Dict[str, str]] = {
    "main_menu_prompt": {
        "ru": "Shymkent Dendrosayabaq",
        "kz": "Shymkent Dendrosayabaq",
        "en": "Shymkent Dendrosayabaq"
    },
    "choose_language": {
        "ru": "Тілді таңдаңыз / Выберите язык / Choose language",
        "kz": "Тілді таңдаңыз / Выберите language / Choose language",
        "en": "Please choose a language"
    },
    "quiz_start": {
        "ru": "Викторина началась!",
        "kz": "Викторина басталды!",
        "en": "Quiz started!"
    },
    "quiz_finished": {
        "ru": "Викторина завершена. Ваш счёт: {score}/{total}.",
        "kz": "Викторина аяқталды. Сіздің ұпайыңыз: {score}/{total}.",
        "en": "Quiz finished. Your score: {score}/{total}."
    },
    "quiz_exit_confirm": {
        "ru": "Викторина остановлена.",
        "kz": "Викторина тоқтатылды.",
        "en": "Quiz stopped."
    },
    "answer_correct": {
        "ru": "Правильно!",
        "kz": "Дұрыс!",
        "en": "Correct!"
    },
    "answer_wrong": {
        "ru": "Неправильно. Правильный ответ: {answer}. {ex}",
        "kz": "Дұрыс емес. Дұрыс жауап: {answer}. {ex}",
        "en": "Wrong. Correct answer: {answer}. {ex}"
    },
    "pick_from_buttons": {
        "ru": "Пожалуйста, выберите вариант кнопкой.",
        "kz": "Түймешені пайдаланып жауап таңдаңыз.",
        "en": "Please pick an option using the buttons."
    }
}

def t(lang: str, key: str, **kwargs) -> str:
    """
    Safe translator helper.
    - Returns fallback values if a key/lang are missing.
    - Logs missing translations and returns a visible placeholder if not found.
    """
    lang = lang if lang in ("ru", "kz", "en") else "ru"
    s = STRINGS.get(key, {}).get(lang)
    if not s:
        s = STRINGS.get(key, {}).get("ru")
    if not s:
        logging.warning("i18n miss: key=%s lang=%s", key, lang)
        s = f"[{key}]"
    if kwargs:
        try:
            return s.format(**kwargs)
        except Exception:
            return s
    return s