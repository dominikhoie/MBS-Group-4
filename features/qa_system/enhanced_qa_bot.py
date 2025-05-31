import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from qa_database import get_enhanced_response, get_accessibility_info
from utils.language import detect_language

import os
from dotenv import load_dotenv

# qa_database.py
import sys
import os
print("Current working directory:", os.getcwd())
print("Python path:", sys.path)

try:
    from utils.language import detect_language
    print("Successfully imported detect_language")
except ImportError as e:
    print(f"Import error: {e}")
    # 添加当前目录到路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    from utils.language import detect_language
    print("Successfully imported after adding to path")

logging.basicConfig(level=logging.INFO)

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
if BOT_TOKEN is None:
    raise ValueError("Bot token not set")
BOT_NAME = os.getenv('BOT_NAME')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# Quick response buttons
def get_quick_response_keyboard(language: str = "en"):
    """Create quick response keyboard based on language"""
    
    if language == "de":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🕘 Öffnungszeiten", callback_data="hours_de"),
                InlineKeyboardButton(text="🎢 Einrichtungen", callback_data="facilities_de")
            ],
            [
                InlineKeyboardButton(text="☕ Café", callback_data="cafe_de"),
                InlineKeyboardButton(text="♿ Barrierefreiheit", callback_data="accessibility_de")
            ],
            [
                InlineKeyboardButton(text="🛡️ Sicherheit", callback_data="safety_de"),
                InlineKeyboardButton(text="🥗 Vegetarisch", callback_data="vegetarian_de")
            ]
        ])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🕘 Opening Hours", callback_data="hours_en"),
                InlineKeyboardButton(text="🎢 Facilities", callback_data="facilities_en")
            ],
            [
                InlineKeyboardButton(text="☕ Café", callback_data="cafe_en"),
                InlineKeyboardButton(text="♿ Accessibility", callback_data="accessibility_en")
            ],
            [
                InlineKeyboardButton(text="🛡️ Safety", callback_data="safety_en"),
                InlineKeyboardButton(text="🥗 Vegetarian", callback_data="vegetarian_en")
            ]
        ])
    
    return keyboard

# /start command
@router.message(Command("start"))
async def send_welcome(message: types.Message):
    if message.text:
        user_language = detect_language(message.text) if len(message.text) > 6 else "en"
    
    if user_language == "de":
        welcome_text = """🎉 Willkommen beim Bamboolino Spielplatz Bot!

🤖 Ich bin Ihr intelligenter Assistent und kann Ihnen helfen mit:
• 🕘 Öffnungszeiten und Buchungen
• 🎢 Informationen über Einrichtungen
• ☕ Café und Speiseoptionen
• ♿ Barrierefreiheit und Zugänglichkeit
• 🛡️ Sicherheitsinformationen

💬 Stellen Sie mir eine Frage oder wählen Sie eine Option unten:"""
    else:
        welcome_text = """🎉 Welcome to the Bamboolino Playground Bot!

🤖 I'm your intelligent assistant and can help you with:
• 🕘 Opening hours and bookings
• 🎢 Facility information
• ☕ Café and food options
• ♿ Accessibility and accommodation
• 🛡️ Safety information

💬 Ask me a question or choose an option below:"""
    
    keyboard = get_quick_response_keyboard(user_language)
    await message.reply(welcome_text, reply_markup=keyboard)

# Handle callback queries from inline buttons
@router.callback_query()
async def handle_callback_query(callback_query: types.CallbackQuery):
    data = callback_query.data
    if data:
        language = data.split('_')[-1]  # Extract language from callback data
        topic = data.replace(f'_{language}', '')  # Extract topic
    
    # Map callback data to query text
    query_map = {
        "hours": "opening hours",
        "facilities": "facilities",
        "cafe": "café",
        "accessibility": "accessibility",
        "safety": "safety",
        "vegetarian": "vegetarian"
    }
    
    if topic in query_map:
        if topic == "accessibility":
            response = get_accessibility_info("general accessibility", language)
        else:
            response = get_enhanced_response(query_map[topic], str(callback_query.from_user.id))
        
        await callback_query.message.edit_text(response, reply_markup=get_quick_response_keyboard(language))
    
    await callback_query.answer()

# Handle text messages
@router.message()
async def handle_message(message: types.Message):
    if message.text:
        user_text = message.text.strip()
        user_id = str(message.from_user.id)
        
        # Check if it's an accessibility-related query
        accessibility_keywords = [
            "accessibility", "disabled", "wheelchair", "barrierefreiheit", "behindert", "rollstuhl",
            "autism", "autismus", "sensory", "sensorisch", "quiet", "ruhig"
        ]
        
        if any(keyword in user_text.lower() for keyword in accessibility_keywords):
            language = detect_language(user_text)
            response = get_accessibility_info(user_text, language)
            keyboard = get_quick_response_keyboard(language)
            await message.reply(response, reply_markup=keyboard)
        else:
            response = get_enhanced_response(user_text, user_id)
            language = detect_language(user_text)
            keyboard = get_quick_response_keyboard(language)
            await message.reply(response, reply_markup=keyboard)

# Help command
@router.message(Command("help"))
async def send_help(message: types.Message):
    language = detect_language(message.text) if len(message.text) > 5 else "en"
    
    if language == "de":
        help_text = """🤖 Bamboolino Bot Hilfe

📝 Verfügbare Befehle:
• /start - Bot starten
• /help - Diese Hilfe anzeigen
• /accessibility - Barrierefreiheit-Informationen

💬 Sie können mir Fragen stellen über:
• Öffnungszeiten und Geschäftszeiten
• Spielplatz-Einrichtungen und Geräte
• Café, Essen und Getränke
• Vegetarische und vegane Optionen
• Sicherheitsmaßnahmen
• Barrierefreiheit und Rollstuhlzugang
• Sensorfreundliche Bereiche

✨ Beispiele:
• "Welche Öffnungszeiten habt ihr?"
• "Gibt es rollstuhlgerechte Zugänge?"
• "Habt ihr vegetarisches Essen?"
"""
    else:
        help_text = """🤖 Bamboolino Bot Help

📝 Available Commands:
• /start - Start the bot
• /help - Show this help
• /accessibility - Accessibility information

💬 You can ask me about:
• Opening hours and business times
• Playground facilities and equipment
• Café, food and drinks
• Vegetarian and vegan options
• Safety measures
• Accessibility and wheelchair access
• Sensory-friendly areas

✨ Examples:
• "What are your opening hours?"
• "Do you have wheelchair access?"
• "Do you have vegetarian food?"
"""
    
    keyboard = get_quick_response_keyboard(language)
    await message.reply(help_text, reply_markup=keyboard)

@router.message(Command("accessibility"))
async def send_accessibility_info(message: types.Message):
    language = detect_language(message.text) if len(message.text) > 13 else "en"
    response = get_accessibility_info("general accessibility", language)
    keyboard = get_quick_response_keyboard(language)
    await message.reply(response, reply_markup=keyboard)

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())