import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import os

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("✅ Бот работает и запущен на сервере")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
