from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def lang_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇰🇿 Қазақша")],
            [KeyboardButton(text="🇷🇺 Русский")],
            [KeyboardButton(text="🇬🇧 English")]
        ],
        resize_keyboard=True
    )

def main_menu_kb(lang: str = "ru"):
    if lang == "kz":
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🧪 Викторина")],
                [KeyboardButton(text="ℹ️ Ақпарат")],
                [KeyboardButton(text="👤 Профиль")],
                [KeyboardButton(text="🆘 SOS")],
                [KeyboardButton(text="🌐 Тіл")]
            ],
            resize_keyboard=True
        )
    if lang == "en":
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🧪 Quiz")],
                [KeyboardButton(text="ℹ️ Info")],
                [KeyboardButton(text="👤 Profile")],
                [KeyboardButton(text="🆘 SOS")],
                [KeyboardButton(text="🌐 Language")]
            ],
            resize_keyboard=True
        )
    # default ru
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🧪 Викторина")],
            [KeyboardButton(text="ℹ️ Инфо")],
            [KeyboardButton(text="👤 Профиль")],
            [KeyboardButton(text="🆘 SOS")],
            [KeyboardButton(text="🌐 Язык")]
        ],
        resize_keyboard=True
    )

def info_options_kb(lang: str = "ru"):
    # Убрана кнопка "🔙 Назад" — оставлена только кнопка "Главное меню" / "Басты мәзір" / "Main menu"
    if lang == "kz":
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📍 Орналасқан жері")],
                [KeyboardButton(text="🕒 Жұмыс уақыты")],
                [KeyboardButton(text="📜 Ережелер"), KeyboardButton(text="🌿 Көрікті жерлер")],
                [KeyboardButton(text="🏠 Басты мәзір")]
            ],
            resize_keyboard=True
        )
    if lang == "en":
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📍 Location")],
                [KeyboardButton(text="🕒 Opening hours")],
                [KeyboardButton(text="📜 Rules"), KeyboardButton(text="🌿 Sights")],
                [KeyboardButton(text="🏠 Main menu")]
            ],
            resize_keyboard=True
        )
    # default ru
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Адрес")],
            [KeyboardButton(text="🕒 Время работы")],
            [KeyboardButton(text="📜 Правила"), KeyboardButton(text="🌿 Красивые места")],
            [KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True
    )

def sights_kb(lang: str = "ru"):
    if lang == "kz":
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🌿 1. Орталық аллея")],
                [KeyboardButton(text="🌸 2. Гүлзарлар")],
                [KeyboardButton(text="🌲 3. Қылқан жапырақтылар")],
                [KeyboardButton(text="🌳 4. Экзотикалық ағаштар")],
                [KeyboardButton(text="🏞️ 5. Көл мен арналары")],
                [KeyboardButton(text="🚲 6. Веложолдар")],
                [KeyboardButton(text="🕊️ 7. Демалыс аймақтары")],
                [KeyboardButton(text="📸 8. Фото-аймақтар")],
                [KeyboardButton(text="🌺 9. Асқаров бұрышы")],
                [KeyboardButton(text="🌅 10. Күн бату көрінісі")],
                [KeyboardButton(text="🔙 Артқа"), KeyboardButton(text="🏠 Басты мәзір")]
            ],
            resize_keyboard=True
        )
    if lang == "en":
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🌿 1. Central alley")],
                [KeyboardButton(text="🌸 2. Flowerbeds")],
                [KeyboardButton(text="🌲 3. Conifer alley")],
                [KeyboardButton(text="🌳 4. Exotic trees")],
                [KeyboardButton(text="🏞️ 5. Pond and channels")],
                [KeyboardButton(text="🚲 6. Paths and bike lanes")],
                [KeyboardButton(text="🕊️ 7. Recreation areas")],
                [KeyboardButton(text="📸 8. Photo spots")],
                [KeyboardButton(text="🌺 9. Askarov corner")],
                [KeyboardButton(text="🌅 10. Sunset view")],
                [KeyboardButton(text="🔙 Back"), KeyboardButton(text="🏠 Main menu")]
            ],
            resize_keyboard=True
        )
    # ru
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌿 1. Центральная аллея")],
            [KeyboardButton(text="🌸 2. Цветники")],
            [KeyboardButton(text="🌲 3. Аллея хвойных")],
            [KeyboardButton(text="🌳 4. Экзотические деревья")],
            [KeyboardButton(text="🏞️ 5. Озеро и каналы")],
            [KeyboardButton(text="🚲 6. Пешеходные и велодорожки")],
            [KeyboardButton(text="🕊️ 7. Зоны отдыха")],
            [KeyboardButton(text="📸 8. Фотозоны")],
            [KeyboardButton(text="🌺 9. Уголок Асқарова")],
            [KeyboardButton(text="🌅 10. Вид на закат")],
            [KeyboardButton(text="🔙 Назад"), KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True
    )