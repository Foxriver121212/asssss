from pathlib import Path
import logging
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from keyboards.main_kb import info_options_kb, main_menu_kb, sights_kb
from services.db import ensure_user, get_user_lang
from services.i18n import t

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()

# --------------------------
# Базовая директория и папка с изображениями (универсально при переносе проекта)
# --------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
IMAGES_DIR = (BASE_DIR / "images").resolve()
logger.info("Images dir resolved to: %s", IMAGES_DIR)

# --------------------------
# Собираем маппинг 1..10 -> Path|None (поддержка разных расширений и постфикса _fixed)
# --------------------------
IMAGE_BY_INDEX: dict[str, Path | None] = {}
for i in range(1, 11):
    found = None
    # сначала пробуем явно указанные варианты
    for cand_name in (f"{i}_fixed.jpg", f"{i}.jpg", f"{i}.jpeg", f"{i}.png", f"{i}.webp", f"{i}.bmp"):
        cand = IMAGES_DIR / cand_name
        if cand.exists() and cand.is_file():
            found = cand
            break
    # fallback: любой файл, начинающийся с индекса (например "1-portrait.png")
    if not found and IMAGES_DIR.exists():
        for candidate in sorted(IMAGES_DIR.glob(f"{i}*")):
            if candidate.is_file():
                found = candidate
                break
    IMAGE_BY_INDEX[str(i)] = found
    logger.info("Mapping image %s -> %s", i, found)

# --------------------------
# Тексты и данные
# --------------------------
INFO_TEXTS = {
    "about": {
        "kz": (
            "ДЕНДРОСАЯБАҚ ТУРАЛЫ АҚПАРАТ\n\n"
            "ЖАЛПЫ МӘЛІМЕТ:\n"
            "АТАУЫ: Асанбай Асқаров атындағы Шымкент дендросаябағы.\n"
            "АШЫЛҒАН ЖЫЛЫ: 1979 ЖЫЛ\n"
            "ЖАЛПЫ КӨЛЕМІ: 117 га\n"
            "Ағаштар саны — 500 мыңнан астам. Шөптесін өсімдіктер саны — 1 360 000."
        ),
        "ru": (
            "ИНФОРМАЦИЯ О ДЕНДРОПАРКЕ\n\n"
            "ОБЩИЕ СВЕДЕНИЯ:\n"
            "НАЗВАНИЕ: Шымкентский дендросад имени Асанбая Аскарова.\n"
            "ОТКРЫТ: 1979 ГОД\n"
            "ПЛОЩАДЬ: 117 га\n"
            "Количество деревьев — более 500 000. Количество травянистых растений — 1 360 000."
        ),
        "en": (
            "ABOUT THE DENDRO PARK\n\n"
            "GENERAL INFO:\n"
            "NAME: Shymkent Dendro Park named after Asanbay Askarov.\n"
            "OPENED: 1979\n"
            "AREA: 117 ha\n"
            "Number of trees — over 500,000. Herbaceous plants — 1,360,000."
        )
    },
    "hours_and_price": {
        "kz": "Жұмыс уақыты: күн сайын 05:00 — 01:00\nБилет: 100 ₸ (кемтарлар, зейнеткерлер, көпбалалы отбасылар мен мектеп оқушыларына кіру тегін).",
        "ru": "Время работы: ежедневно 05:00 — 01:00\nБилет: 100 ₸ (вход бесплатный для ветераанов, людей с инвалидностью, пенсионеров, многодетных и школьников).",
        "en": "Opening hours: daily 05:00 — 01:00\nTicket: 100 KZT (free entry for veterans, people with disabilities, pensioners, large families and schoolchildren)."
    },
    "address_and_transport": {
        "kz": (
            "Мекенжай: Шымкент қаласы, Байдибек би даңғылы, 108/10\nКоординаттар: 42.370540, 69.616596\n\n"
            "Қоғамдық көлік: автобус бағыттары — 16, 27, 65, 45, 147 (тоқтайтын аялдама: «Дендросаябақ» немесе «Асқаров паркі»)."
        ),
        "ru": (
            "Адрес: г. Шымкент, пр. Байдибек би, 108/10\nКоординаты: 42.370540, 69.616596\n\n"
            "Общественный транспорт: автобусы 16, 27, 65, 45, 147 (остановка «Дендросад» или «Парк Аскарова»)."
        ),
        "en": (
            "Address: Baydibek Bi Ave 108/10, Shymkent\nCoordinates: 42.370540, 69.616596\n\n"
            "Public transport: buses 16, 27, 65, 45, 147 (stop «Dendropark» or «Asqarov Park»)."
        )
    }
}

PARK_RULES = {
    "kz": (
        "Дендросаябақта тәртіп сақтау ережелері:\n\n"
        "• дәрілік шөптерді жинауға тыйым салынады;\n"
        "• от жағуға тыйым салынады;\n"
        "• ағаштарды қырқуға тыйым салынады;\n"
        "• аң мен құсты аулауға тыйым салынады;\n"
        "• балық ұстауға тыйым салынады;\n"
        "• демалған жерде тамақ қалдықтары мен күл-қоқысты қалдыруға болмайды."
    ),
    "ru": (
        "Правила поведения в дендросаду:\n\n"
        "• запрещено собирать лекарственные травы;\n"
        "• запрещено разводить огонь;\n"
        "• запрещено обрезать деревья;\n"
        "• запрещено охотиться на животных и птиц;\n"
        "• запрещено ловить рыбу;\n"
        "• запрещено оставлять пищевые отходы и мусор."
    ),
    "en": (
        "Park rules:\n\n"
        "• do not collect medicinal herbs;\n"
        "• do not light fires;\n"
        "• do not cut trees;\n"
        "• do not hunt animals or birds;\n"
        "• do not fish;\n"
        "• do not leave food waste or trash."
    )
}

SIGHTS_DETAILS = {
    "kz": {
        "🌿 1. Орталық аллея": (
            "🌿 1. Орталық аллея (кіреберіс бөлігі)\n\n"
            "Кіреберістен бастап ұзын орталық аллея бойымен сәнді ағаштар, гүлзарлар және көгалдар орналасқан. "
            "Мұнда Асанбай Асқаровтың ескерткіші орнатылған — бұл жер саябақтың символына айналған. "
            "Суретке түсуге ең жиі таңдалатын орындардың бірі."
        ),
        "🌸 2. Гүлзарлар": (
            "🌸 2. Гүлзарлар мен гүлді алаңдар\n\n"
            "Көктем мен жаз мезгілінде саябақ ішін раушан, қызғалдақ, бегония, лаванда сияқты түрлі-түсті гүлдер безендіреді. "
            "Гүлзарлардың кейбірі геометриялық немесе ұлттық өрнек түрінде отырғызылған."
        ),
        "🌲 3. Қылқан жапырақтылар": (
            "🌲 3. Қылқан жапырақты ағаштар аллеясы\n\n"
            "Мұнда арша, шырша, қарағай, самырсын сияқты сирек кездесетін қылқан жапырақты ағаш түрлері өседі. "
            "Ауа ерекше таза әрі хош иісті — демалуға және тыныс алу жаттығуларына таптырмас жер."
        ),
        "🌳 4. Экзотикалық ағаштар": (
            "🌳 4. Экзотикалық ағаштар мен ботаникалық аймақ\n\n"
            "Әлемнің әр бұрышынан әкелінген ағаш түрлері бар: Италия, Қытай, Корея, Кавказ елдерінен отырғызылған. "
            "Сиверс алмасы мен недзвецкий алмасы — Қазақстанның Қызыл кітабына енген ерекше өсімдіктердің бірі."
        ),
        "🏞️ 5. Көл мен арналары": (
            "🏞️ 5. Көл мен су арналары\n\n"
            "Саябақ аумағында жасанды шағын көл мен арық жүйесі бар. "
            "Көктемде және жазда бұл жерде үйректер мен қаздар жүзіп жүреді, ал судың бойында тынығуға арналған орындықтар мен көпіршелер орнатылған."
        ),
        "🚲 6. Веложолдар": (
            "🚲 6. Жаяу және веложолдар\n\n"
            "Көптеген веложолдар мен серуен соқпақтары бар. "
            "Ағаштардың көлеңкесінде жүру өте жайлы, әсіресе жаздың ыстығында. Кешке жарық шамдармен көмкеріліп, ерекше атмосфера тудырады."
        ),
        "🕊️ 7. Демалыс аймақтары": (
            "🕊️ 7. Тынығу және демалыс аймақтары\n\n"
            "Арнайы отбасылық демалысқа арналған алаңдар, балалар ойын алаңшалары, орындықтар мен беседкалар көп. "
            "Кей аймақтарда йога және фитнес жаттығулары үшін алаңдар қарастырылған."
        ),
        "📸 8. Фото-аймақтар": (
            "8. Фото-аймақтар мен көрме алаңдары\n\n"
            "Белгілі бір мезгілдерде (көктем, күз) саябақта табиғат көрмелері, экологиялық акциялар және гүл фестивальдері өткізіледі. "
            "Көптеген блогерлер мен жас жұбайлар фото және видео түсірілімге осы жерді таңдайды."
        ),
        "🌺 9. Асқаров бұрышы": (
            "🌺 9. Асқаровтың еңбегін еске алу бұрышы\n\n"
            "Бұл арнайы бөлімде Асанбай Асқаровтың өмірі мен еңбегін таныстыратын ақпараттық тақталар мен стендтер орналасқан. "
            "Шымкенттің “жасыл қала” болып қалыптасуына оның қосқан үлесі ерекше."
        ),
        "🌅 10. Күн бату көрінісі": (
            "🌅 10. Күн батқан кездегі көрініс\n\n"
            "Кешке қарай күн сәулесі ағаштар арасынан өтіп, ерекше алтын түске боялады. Бұл мезгіл — саябақтың ең суретке әдемі түсетін сәті."
        )
    },
    "ru": {
        "🌿 1. Центральная аллея": (
            "🌿 1. Центральная аллея (входная часть)\n\n"
            "От входа тянется длинная центральная аллея с декоративными деревьями, цветниками и газонами. "
            "Здесь установлен памятник Асанбаю Аскарову — один из символов парка. Часто выбираемое место для фотографий."
        ),
        "🌸 2. Цветники": (
            "🌸 2. Цветники и цветочные площадки\n\n"
            "Весной и летом парк украшен розами, тюльпанами, бегонией, лавандой. Некоторые цветники высажены в геометрические или национальные узоры."
        ),
        "🌲 3. Аллея хвойных": (
            "🌲 3. Аллея хвойных\n\n"
            "Здесь растут можжевельник, ель, сосна, пихта и другие редкие хвойные виды. Воздух особенно чистый и ароматный — отличное место для отдыха и дыхательных упражнений."
        ),
        "🌳 4. Экзотические деревья": (
            "🌳 4. Экзотические деревья и ботаническая зона\n\n"
            "В парке представлены деревья из Италии, Китая, Кореи и стран Кавказа. Сиверс и недзвецкий яблоки — редкие виды, включённые в Красную книгу Казахстана."
        ),
        "🏞️ 5. Озеро и каналы": (
            "🏞️ 5. Озеро и водные каналы\n\n"
            "На территории парка есть искусственный пруд и система каналов. Весной и летом здесь плавают утки и гуси; у воды установлены скамейки и мостики."
        ),
        "🚲 6. Пешеходные и велодорожки": (
            "🚲 6. Пешеходные и велодорожки\n\n"
            "Много велодорожек и тропинок для прогулок. Ходить в тени деревьев особенно приятно в жару; вечером дорожки подсвечиваются."
        ),
        "🕊️ 7. Зоны отдыха": (
            "🕊️ 7. Зоны отдыха\n\n"
            "Семейные зоны отдыха, детские площадки, скамейки и беседки. Есть площадки для йоги и фитнеса."
        ),
        "📸 8. Фотозоны": (
            "8. Фотозоны и выставочные площадки\n\n"
            "В парке регулярно проходят природные выставки, экологические акции и цветочные фестивали. Многие блогеры и молодожёны выбирают это место для съёмок."
        ),
        "🌺 9. Уголок Асқарова": (
            "🌺 9. Уголок памяти Аскарова\n\n"
            "Информационные стенды и таблички рассказывают о жизни и вкладе Асанбая Аскарова в развитие зелёного облика Шымкента."
        ),
        "🌅 10. Вид на закат": (
            "🌅 10. Вид на закат\n\n"
            "На закате солнце пробивается сквозь кроны деревьев и окрашивает парк в тёплые золотые тона — одно из самых живописных зрелищ."
        )
    },
    "en": {
        "🌿 1. Central alley": (
            "🌿 1. Central alley (entrance area)\n\n"
            "From the entrance a long central alley stretches with ornamental trees, flowerbeds and lawns. "
            "The Asanbay Askarov monument is located here — a popular photo spot."
        ),
        "🌸 2. Flowerbeds": (
            "🌸 2. Flowerbeds and floral areas\n\n"
            "In spring and summer the park is decorated with roses, tulips, begonia and lavender. Some flowerbeds are planted in geometric or national patterns."
        ),
        "🌲 3. Conifer alley": (
            "🌲 3. Conifer alley\n\n"
            "Juniper, spruce, pine and fir grow here, among other rare conifers. The air is especially clean and fragrant."
        ),
        "🌳 4. Exotic trees": (
            "🌳 4. Exotic trees and botanical area\n\n"
            "Species from Italy, China, Korea and the Caucasus are represented. Some rare apple varieties in the park are included in Kazakhstan's Red Book."
        ),
        "🏞️ 5. Pond and channels": (
            "🏞️ 5. Pond and water channels\n\n"
            "The park has an artificial pond and canal system. Ducks and geese swim here in spring and summer; benches and small bridges make it a romantic photo spot."
        ),
        "🚲 6. Paths and bike lanes": (
            "🚲 6. Walking and cycling paths\n\n"
            "Many bike paths and walking trails are available. Walking in the shade is pleasant in hot weather; paths are lit in the evening."
        ),
        "🕊️ 7. Recreation areas": (
            "🕊️ 7. Recreation areas\n\n"
            "Family recreation zones, playgrounds, benches and gazebos. Some areas are designed for yoga and fitness."
        ),
        "📸 8. Photo spots": (
            "8. Photo spots and exhibition areas\n\n"
            "The park regularly hosts nature exhibitions, eco-actions and flower festivals. Many bloggers and newlyweds choose this place for shoots."
        ),
        "🌺 9. Askarov corner": (
            "🌺 9. Askarov memorial corner\n\n"
            "Informational stands tell about Asanbay Askarov's life and his contribution to Shymkent's green development."
        ),
        "🌅 10. Sunset view": (
            "🌅 10. Sunset view\n\n"
            "At sunset sunlight filters through the trees and paints the park in warm golden tones — one of the most picturesque sights."
        )
    }
}

SOS_TEXT = {
    "kz": (
        "🚒 101 – Өрт сөндіру және құтқару қызметі\n"
        "👮 102 – Полиция\n"
        "🚑 103 – Жедел жәрдем\n"
        "⚡ 104 – Газ қызметі (төтенше жағдайлар кезінде)\n"
        "💧 105 – Су арнасы (су құбырлары апаты, ақау)\n"
        "📞 109 – Бірыңғай байланыс орталығы\n"
        "📡 112 – Бірыңғай төтенше жағдайлар қызметі"
    ),
    "ru": (
        "🚒 101 – Пожарная и спасательная служба\n"
        "👮 102 – Полиция\n"
        "🚑 103 – Скорая помощь\n"
        "⚡ 104 – Газовая служба\n"
        "💧 105 – Водоканал\n"
        "📞 109 – Единый контакт-центр\n"
        "📡 112 – Единый номер экстренных служб"
    ),
    "en": (
        "🚒 101 – Fire and Rescue Service\n"
        "👮 102 – Police\n"
        "🚑 103 – Ambulance\n"
        "⚡ 104 – Gas service\n"
        "💧 105 – Water utility\n"
        "📞 109 – Unified contact center\n"
        "📡 112 – Unified emergency number"
    )
}

# --------------------------
# Обработчики
# --------------------------
@router.message(F.text == "ℹ️ Инфо")
@router.message(F.text == "ℹ️ Info")
@router.message(F.text == "ℹ️ Ақпарат")
async def cmd_info(message: Message):
    ensure_user(message.from_user.id, message.from_user.username or "", message.from_user.first_name or "")
    lang = get_user_lang(message.from_user.id)
    header = t(lang, "main_menu_prompt")
    await message.answer(header + "\n\n" + INFO_TEXTS["about"].get(lang, INFO_TEXTS["about"]["ru"]),
                         reply_markup=info_options_kb(lang=lang))


@router.message(F.text == "📍 Адрес")
@router.message(F.text == "📍 Орналасқан жері")
@router.message(F.text == "📍 Location")
async def cmd_address(message: Message):
    lang = get_user_lang(message.from_user.id)
    await message.answer(INFO_TEXTS["address_and_transport"].get(lang, INFO_TEXTS["address_and_transport"]["ru"]),
                         reply_markup=info_options_kb(lang=lang))


@router.message(F.text == "🕒 Время работы")
@router.message(F.text == "🕒 Жұмыс уақыты")
@router.message(F.text == "🕒 Opening hours")
async def cmd_hours(message: Message):
    lang = get_user_lang(message.from_user.id)
    await message.answer(INFO_TEXTS["hours_and_price"].get(lang, INFO_TEXTS["hours_and_price"]["ru"]),
                         reply_markup=info_options_kb(lang=lang))


@router.message(F.text == "📜 Правила")
@router.message(F.text == "📜 Rules")
@router.message(F.text == "📜 Ережелер")
async def cmd_rules(message: Message):
    ensure_user(message.from_user.id, message.from_user.username or "", message.from_user.first_name or "")
    lang = get_user_lang(message.from_user.id)
    await message.answer(PARK_RULES.get(lang, PARK_RULES["ru"]), reply_markup=info_options_kb(lang=lang))


# SOS handler: отправляет текст без изменения клавиатуры
@router.message(F.text == "🆘 SOS")
async def cmd_sos(message: Message):
    try:
        ensure_user(message.from_user.id, message.from_user.username or "", message.from_user.first_name or "")
        lang = get_user_lang(message.from_user.id)
        sos_text = SOS_TEXT.get(lang, SOS_TEXT["ru"])
        logger.info("cmd_sos triggered by user=%s text=%r", message.from_user.id, message.text)
        await message.answer(sos_text)  # клавиатура не меняется
    except Exception:
        logger.exception("Error in cmd_sos")


@router.message(F.text == "🌿 Көрікті жерлер")
@router.message(F.text == "🌿 Sights")
@router.message(F.text == "🌿 Красивые места")
async def cmd_sights_menu(message: Message):
    lang = get_user_lang(message.from_user.id)
    await message.answer(t(lang, "main_menu_prompt"), reply_markup=sights_kb(lang=lang))


# --------------------------
# Фильтрующий обработчик для нажатий на кнопки 1..10 меню "Көрікті жерлер"
# --------------------------
SIGHT_BUTTON_TEXTS = set()
for lang_map in SIGHTS_DETAILS.values():
    for key in lang_map.keys():
        SIGHT_BUTTON_TEXTS.add(key)

NAV_SET = {
    "🔙 Назад", "🔙 Артқа", "🔙 Back",
    "🏠 Главное меню", "🏠 Басты мәзір", "🏠 Main menu"
}


@router.message(F.text.in_(SIGHT_BUTTON_TEXTS.union(NAV_SET)))
async def cmd_sight_detail_filtered(message: Message):
    text = (message.text or "").strip()
    lang = get_user_lang(message.from_user.id) or "ru"

    # навигация
    if text in ("🔙 Артқа", "🔙 Back", "🔙 Назад"):
        await message.answer(t(lang, "main_menu_prompt"), reply_markup=info_options_kb(lang=lang))
        return
    if text in ("🏠 Басты мәзір", "🏠 Main menu", "🏠 Главное меню"):
        await message.answer(t(lang, "main_menu_prompt"), reply_markup=main_menu_kb(lang=lang))
        return

    details_map = SIGHTS_DETAILS.get(lang, SIGHTS_DETAILS.get("ru", {}))
    if text in details_map:
        caption = details_map[text]
        # извлекаем индекс из текста
        maybe = "".join(ch for ch in text if ch.isdigit())
        idx = maybe if maybe in [str(n) for n in range(1, 11)] else None

        img_path = IMAGE_BY_INDEX.get(idx)
        # логирование о наличии файла
        if not img_path:
            logger.warning("No image mapped for idx=%s", idx)
        elif not img_path.exists():
            logger.warning("Mapped image missing on disk: %s", img_path)
        else:
            try:
                size = img_path.stat().st_size
                logger.info("Attempt to send image %s size=%d", img_path, size)
                photo = FSInputFile(str(img_path.resolve()))
                await message.answer_photo(photo=photo, caption=caption, reply_markup=sights_kb(lang=lang))
                return
            except Exception as e:
                logger.exception("Failed to send as photo %s: %s", img_path, e)
                try:
                    doc = FSInputFile(str(img_path.resolve()))
                    await message.answer_document(document=doc, caption=caption, reply_markup=sights_kb(lang=lang))
                    return
                except Exception as e2:
                    logger.exception("Failed document fallback for %s: %s", img_path, e2)
                    await message.answer("Файл недоступен для отправки. Попробуйте позже.", reply_markup=sights_kb(lang=lang))
                    return

        # если файла нет или не найден — просто отправляем текст
        await message.answer(caption, reply_markup=sights_kb(lang=lang))
        return

    # если ключ не совпал по локали — попытка найти по номеру в любом языке
    maybe = "".join(ch for ch in text if ch.isdigit())
    if maybe and maybe in [str(n) for n in range(1, 11)]:
        idx = maybe
        caption_map = {}
        for lg in ("kz", "ru", "en"):
            for key, val in SIGHTS_DETAILS.get(lg, {}).items():
                if str(idx) in key:
                    caption_map[lg] = val
                    break
        caption = caption_map.get(lang) or caption_map.get("ru") or ""
        img_path = IMAGE_BY_INDEX.get(idx)
        if img_path and img_path.exists():
            try:
                photo = FSInputFile(str(img_path.resolve()))
                await message.answer_photo(photo=photo, caption=caption, reply_markup=sights_kb(lang=lang))
                return
            except Exception as e:
                logger.exception("Failed to send photo %s as image, will try as document: %s", img_path, e)
                try:
                    doc = FSInputFile(str(img_path.resolve()))
                    await message.answer_document(document=doc, caption=caption, reply_markup=sights_kb(lang=lang))
                    return
                except Exception as e2:
                    logger.exception("Failed document fallback for %s: %s", img_path, e2)
                    await message.answer("Файл недоступен для отправки. Попробуйте позже.", reply_markup=sights_kb(lang=lang))
                    return
        await message.answer(caption or "Информация временно недоступна.", reply_markup=sights_kb(lang=lang))
        return

# --------------------------
# Конец файла
# --------------------------