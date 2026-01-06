import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 8080))

bot = Bot(token=TOKEN)
dp = Dispatcher()

def main_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="➕ Добавить")],
            [types.KeyboardButton(text="📄 Показать")]
        ],
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Выбери действие:",
        reply_markup=main_keyboard()
    )

@dp.message(lambda m: m.text == "➕ Добавить")
async def add_button(message: types.Message):
    await message.answer("Кнопка добавления (позже будет логика)")

@dp.message(lambda m: m.text == "📄 Показать")
async def show_button(message: types.Message):
    await message.answer("Тут позже будут данные")

# --- КОСТЫЛЬ ДЛЯ RENDER ---
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
