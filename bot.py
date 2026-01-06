import asyncio
import os
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web

# ====== НАСТРОЙКИ ======
TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 8080))

ADMINS = [123456789]  # ← ВСТАВЬ СВОЙ TELEGRAM ID
DB_FILE = "dishes.db"

# ====== INIT ======
bot = Bot(token=TOKEN)
dp = Dispatcher()

db_lock = asyncio.Lock()

# ====== БАЗА ДАННЫХ ======
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            reason TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

async def add_stop(name, date, reason):
    async with db_lock:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO stops (name, date, reason) VALUES (?, ?, ?)",
            (name, date, reason)
        )
        conn.commit()
        conn.close()

async def get_stops():
    async with db_lock:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name, date, reason FROM stops")
        rows = cursor.fetchall()
        conn.close()
        return rows

# ====== ВСПОМОГАТЕЛЬНОЕ ======
def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

# ====== КЛАВИАТУРА ======
def main_keyboard(is_admin_user=False):
    buttons = [[types.KeyboardButton(text="📄 Стоп-лист")]]
    if is_admin_user:
        buttons.append([types.KeyboardButton(text="➕ Поставить на стоп")])
    return types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )

# ====== START ======
@dp.message(Command("start"))
async def start(message: types.Message):
    admin = is_admin(message.from_user.id)
    await message.answer(
        "Выбери действие:",
        reply_markup=main_keyboard(admin)
    )

# ====== ПОКАЗ СТОП-ЛИСТА ======
@dp.message(lambda m: m.text == "📄 Стоп-лист")
async def show_stop(message: types.Message):
    await message.answer("⏳ Загружаю стоп-лист...")

    stops = await get_stops()
    if not stops:
        await message.answer("✅ Сейчас нет блюд на стопе")
        return

    text = ""
    for name, date, reason in stops:
        text += (
            f"🍽 {name}\n"
            f"🔴 Стоп: {date}\n"
            f"Причина: {reason}\n\n"
        )

    await message.answer(text)

# ====== ДОБАВЛЕНИЕ СТОПА ======
@dp.message(lambda m: m.text == "➕ Поставить на стоп")
async def add_stop_start(message: types.Message):
    if not is_admin(message.from_user.id):
        return

    await message.answer(
        "Отправь данные в формате:\n\n"
        "Название / Дата / Причина\n\n"
        "Пример:\n"
        "Эклеры / 21.12 / доработка"
    )

@dp.message(lambda m: "/" in m.text)
async def add_stop_save(message: types.Message):
    if not is_admin(message.from_user.id):
        return

    try:
        name, date, reason = [x.strip() for x in message.text.split("/", 2)]
    except ValueError:
        await message.answer("❌ Неверный формат")
        return

    await add_stop(name, date, reason)
    await message.answer(f"✅ {name} поставлено на стоп")

# ====== КОСТЫЛЬ ДЛЯ RENDER (WEB SERVICE) ======
async def start_web():
    app = web.Application()
    app.router.add_get("/", lambda request: web.Response(text="OK"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

async def start_bot():
    await dp.start_polling(bot)

async def main():
    init_db()
    await asyncio.gather(
        start_bot(),
        start_web()
    )

if __name__ == "__main__":
    asyncio.run(main())

