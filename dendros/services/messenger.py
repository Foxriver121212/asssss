# services/messenger.py
import logging
from typing import Optional
from aiogram.types import Message

async def send_text(message: Message, text: Optional[str], reply_markup=None):
    """
    Safe send helper: prevents sending empty messages.
    If text is empty, logs an error and sends a fallback notice.
    """
    text = (text or "").strip()
    if not text:
        logging.error("Attempt to send empty message to user %s", getattr(message.from_user, "id", "unknown"))
        fallback = "Временно недоступно. Попробуйте позже."
        await message.answer(fallback, reply_markup=reply_markup)
        return
    await message.answer(text, reply_markup=reply_markup)