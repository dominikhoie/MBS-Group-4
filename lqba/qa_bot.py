import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from responses import get_response

import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
if BOT_TOKEN is None:
    raise ValueError("Bot token not set")
BOT_NAME = os.getenv('BOT_NAME')


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# /start
@router.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Welcome to the Bamboolino Playground Bot! 🎉\n"
                        "I can answer questions about playground facilities, opening hours, café menu, vegetarian options, equipment safety, and more.\n"
                        "Please enter your question, for example: 'What are the opening hours?' or 'Do you have a vegetarian menu?'")

# user text messages
@router.message()
async def handle_message(message: types.Message):
    if message.text:
        user_text = message.text.lower().strip()
        response = get_response(user_text) 
        await message.reply(response)

# Start the bot
async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())