import asyncio
import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 8080))

ADMINS = [6293203234]  # ← ВСТАВЬ СВОЙ TELEGRAM ID

DATA_FILE = "dishes.json"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ---------- ВСПОМОГАТЕЛЬНОЕ ----------
def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------- КНОПКИ ----------
def main_keyboard(is_admin_user=False):
    buttons = [[types.KeyboardButton(text="📄 Стоп-лист")]]
    if is_admin_user:
        buttons.append([types.KeyboardButton(text="➕ Поставить на стоп")])
    return types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )

# ---------- КОМАНДЫ ----------
@dp.message(Command("start"))
async def start(message: types.Message):
    admin = is_admin(message.from_user.id)
    await message.answer(
        "Выбери действие:",
        reply_markup=main_keyboard(admin)
    )

# ---------- ПОКАЗ СТОПА ----------
@dp.message(lambda m: m.text == "📄 Стоп-лист")
async def show_stop(message: types.Message):
    data = load_data()
    if not data:
        await message.answer("✅ Сейчас нет блюд на стопе")
        return

    text = ""
    for item in data:
        text += (
            f"🍽 {item['name']}\n"
            f"🔴 Стоп: {item['date']}\n"
            f"Причина: {item['reason']}\n\n"
        )

    await message.answer(text)

# ---------- ДОБАВЛЕНИЕ СТОПА ----------
@dp.message(lambda m: m.text == "➕ Поставить на стоп")
async def add_stop_start(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        "Отправь данные в формате:\n\n"
        "Название | Дата | Причина\n\n"
        "Пример:\n"
        "Эклеры | 21.12 | доработка"
    )

@dp.message(lambda m: "|" in m.text)
async def add_stop_save(message: types.Message):
    if not is_admin(message.from_user.id):
        return

    try:
        name, date, reason = [x.strip() for x in message.text.split("|", 2)]
    except ValueError:
        await message.answer("❌ Неверный формат")
        return

    data = load_data()
    data.append({
        "name": name,
        "date": date,
        "reason": reason
    })
    save_data(data)

    await message.answer(f"✅ {name} поставлено на стоп")

# ---------- КОСТЫЛЬ ДЛЯ RENDER ----------
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
    await asyncio.gather(
        start_bot(),
        start_web()
    )

if __name__ == "__main__":
    asyncio.run(main())
