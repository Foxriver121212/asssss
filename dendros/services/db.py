# services/db.py
import json
import os
from typing import Dict, Any, Optional

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "users.json")
_EVENTS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "events.json")

# В памяти
_users: Dict[str, Dict[str, Any]] = {}

def _ensure_data_dir():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

def _load():
    global _users
    try:
        _ensure_data_dir()
        with open(DB_FILE, "r", encoding="utf-8") as f:
            _users = json.load(f)
    except Exception:
        _users = {}

def _save():
    try:
        _ensure_data_dir()
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(_users, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# Инициализация при импорте
_load()

def _key(user_id: int) -> str:
    return str(user_id)

def ensure_user(user_id: int, username: str = "", name: str = "") -> Dict[str, Any]:
    """Создаёт запись пользователя если её нет и возвращает её."""
    k = _key(user_id)
    if k not in _users:
        _users[k] = {
            "id": user_id,
            "username": username or "",
            "name": name or "",
            "lang": "ru",   # язык по умолчанию
            "quiz": None    # структура: {"active": True, "progress": int, "score": int}
        }
        _save()
    return _users[k]

def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    return _users.get(_key(user_id))

def set_user_lang(user_id: int, lang: str):
    """Установить язык пользователя (kz/ru/en)."""
    ensure_user(user_id)
    if lang not in ("kz", "ru", "en"):
        lang = "ru"
    _users[_key(user_id)]["lang"] = lang
    _save()

def get_user_lang(user_id: int) -> str:
    """Получить язык пользователя. По умолчанию 'ru'."""
    u = get_user(user_id)
    if not u:
        return "ru"
    return u.get("lang", "ru")

# backward compatibility alias
def get_lang(user_id: int) -> str:
    return get_user_lang(user_id)

# ----------------- quiz state helpers -----------------

def start_quiz(user_id: int):
    """Запустить викторину для пользователя (инициализирует состояние)."""
    ensure_user(user_id)
    _users[_key(user_id)]["quiz"] = {"active": True, "progress": 0, "score": 0}
    _save()

def stop_quiz(user_id: int):
    """Остановить викторину (обнулить состояние)."""
    ensure_user(user_id)
    _users[_key(user_id)]["quiz"] = None
    _save()

def is_quiz_active(user_id: int) -> bool:
    u = get_user(user_id)
    return bool(u and u.get("quiz") and u["quiz"].get("active"))

def get_quiz_state(user_id: int) -> Dict[str, int]:
    """Вернуть прогресс и score — безопасно, даже если квиз не активен."""
    u = get_user(user_id)
    if not u or not u.get("quiz"):
        return {"progress": 0, "score": 0}
    q = u["quiz"]
    return {"progress": q.get("progress", 0), "score": q.get("score", 0)}

def advance_quiz(user_id: int, correct: bool):
    """Продвинуть прогресс на 1; увеличить score если correct==True."""
    u = get_user(user_id)
    if not u:
        return
    q = u.get("quiz")
    if not q:
        return
    if correct:
        q["score"] = q.get("score", 0) + 1
    q["progress"] = q.get("progress", 0) + 1
    u["quiz"] = q
    _save()

# ----------------- events helpers -----------------

def _load_events() -> dict:
    try:
        os.makedirs(os.path.dirname(_EVENTS_FILE), exist_ok=True)
        with open(_EVENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"events": []}

def _save_events(data: dict):
    try:
        os.makedirs(os.path.dirname(_EVENTS_FILE), exist_ok=True)
        with open(_EVENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def add_event(event: dict) -> dict:
    """
    Добавить событие. event — словарь с произвольными полями (например: title, date, desc).
    Возвращает сохранённое событие с полем id.
    """
    data = _load_events()
    events = data.get("events", [])
    next_id = 1
    if events:
        try:
            next_id = max([e.get("id", 0) for e in events]) + 1
        except Exception:
            next_id = len(events) + 1
    event_copy = dict(event)
    event_copy["id"] = next_id
    events.append(event_copy)
    data["events"] = events
    _save_events(data)
    return event_copy

def get_events() -> list:
    """Вернуть список всех событий (список словарей)."""
    data = _load_events()
    return data.get("events", [])

def list_users() -> list:
    """Вернуть список всех пользователей (список словарей)."""
    return list(_users.values())

# ----------------- дополнительные утилиты -----------------

def reset_db_file():
    """Утилита для разработки: очищает файл пользователей (не вызывай в проде)."""
    global _users
    _users = {}
    _save()

def get_leaderboard(limit: int = 10) -> list:
    """
    Вернуть топ пользователей по полю quiz.score.
    Возвращает список словарей вида: {"id": id, "username": username, "name": name, "score": score}
    Сортирует по убыванию score и по возрастанию id при равных значениях.
    """
    items = []
    for u in _users.values():
        q = u.get("quiz")
        score = 0
        if q and isinstance(q, dict):
            # если прогресс может превышать длину викторины, используем явное поле score
            score = q.get("score", 0)
        items.append({
            "id": u.get("id"),
            "username": u.get("username", ""),
            "name": u.get("name", ""),
            "score": score
        })
    # сортируем по score desc, затем id asc
    items.sort(key=lambda x: (-int(x.get("score", 0)), int(x.get("id", 0) or 0)))
    return items[:limit]

# Поддержка тестов или внешнего импорта: если нужно — можно обновить или расширить API.