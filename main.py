import asyncio
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from utils.language import detect_language
from features.qa_system.qa_data import get_enhanced_response
from features.accessibility.accessibility_feature import AccessibilityFeature
from features.booking_system.booking_feature import BookingFeature
from utils.text_messages import (
    welcome_text_de, welcome_text_en, help_text_en, help_text_de, 
    contact_text_de, contact_text_en, voice_response_de, voice_response_en,
    location_response_de, location_response_en
)
from utils.voice_processor import VoiceProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables")
BOT_NAME = os.getenv('BOT_NAME', 'BambolinoBot')

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()
router = Router()
voice_processor = VoiceProcessor()

# Initialize features
booking_feature = BookingFeature()
accessibility_feature = AccessibilityFeature()

# main keyboard based on language
def get_main_menu_keyboard(language: str='en') -> InlineKeyboardMarkup:
    if language == "de":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="❓ Fragen & Antworten", callback_data="qa_menu"),
                InlineKeyboardButton(text="🎫 Buchungen", callback_data="booking_menu")
            ],
            [
                InlineKeyboardButton(text="♿ Barrierefreiheit", callback_data="accessibility_menu"),
                InlineKeyboardButton(text="🗺️ Navigation", callback_data="navigation_menu")
            ],
            [
                InlineKeyboardButton(text="📞 Kontakt", callback_data="contact_info"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
            ]
        ])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="❓ Q&A", callback_data="qa_menu"),
                InlineKeyboardButton(text="🎫 Bookings", callback_data="booking_menu")
            ],
            [
                InlineKeyboardButton(text="♿ Accessibility", callback_data="accessibility_menu"),
                InlineKeyboardButton(text="🗺️ Navigation", callback_data="navigation_menu")
            ],
            [
                InlineKeyboardButton(text="📞 Contact", callback_data="contact_info"),
                InlineKeyboardButton(text="🇩🇪 Deutsch", callback_data="lang_de")
            ]
        ])
    return keyboard


def get_quick_response_keyboard(language: str = "en")-> InlineKeyboardMarkup:
    if language == "de":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🕘 Öffnungszeiten", callback_data="qa_hours"),
                InlineKeyboardButton(text="🎢 Einrichtungen", callback_data="qa_facilities")
            ],
            [
                InlineKeyboardButton(text="☕ Café", callback_data="qa_cafe"),
                InlineKeyboardButton(text="🛡️ Sicherheit", callback_data="qa_safety")
            ],
            [
                InlineKeyboardButton(text="🥗 Vegetarisch", callback_data="qa_vegetarian"),
                InlineKeyboardButton(text="🔙 Hauptmenü", callback_data="main_menu")
            ]
        ])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🕘 Opening Hours", callback_data="qa_hours"),
                InlineKeyboardButton(text="🎢 Facilities", callback_data="qa_facilities")
            ],
            [
                InlineKeyboardButton(text="☕ Café", callback_data="qa_cafe"),
                InlineKeyboardButton(text="🛡️ Safety", callback_data="qa_safety")
            ],
            [
                InlineKeyboardButton(text="🥗 Vegetarian", callback_data="qa_vegetarian"),
                InlineKeyboardButton(text="🔙 Main Menu", callback_data="main_menu")
            ]
        ])
    
    return keyboard

# user language preference
user_languages ={}

@router.message(CommandStart())
async def start_command(message: types.Message):
    user_id = message.from_user.id
    
    user_language_code = message.from_user.language_code
    language = "de" if user_language_code and user_language_code.startswith("de") else "en"
    
    user_languages[user_id] = language
    
    if language == "de":
        welcome_text=welcome_text_de
    else:
        welcome_text=welcome_text_en

    keyboard=get_main_menu_keyboard(language)
    await message.answer(welcome_text, reply_markup=keyboard)

@router.message(Command("help"))
async def help_command(message: types.Message):
    user_id = message.from_user.id
    language = user_languages.get(user_id,'en')

    if language=='de':
        help_text=help_text_de
    else:
        help_text=help_text_en

    keyboard=get_main_menu_keyboard(language)
    await message.answer(help_text, reply_markup=keyboard)

@router.callback_query(F.data=="main_menu")
async def main_menu_callback(callback: types.CallbackQuery):
    user_id=callback.from_user.id
    language = user_languages.get(user_id, "en")
    
    text = "🏠 Hauptmenü" if language == "de" else "🏠 Main Menu"
    keyboard = get_main_menu_keyboard(language)

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

#update the language setting
@router.callback_query(F.data.startswith("lang_"))
async def language_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    new_language = callback.data.split("_")[1]
    user_languages[user_id] = new_language

    text = "🏠 Hauptmenü" if new_language == "de" else "🏠 Main Menu"
    keyboard = get_main_menu_keyboard(new_language)

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer("Sprache geändert!" if new_language == "de" else "Language changed!")

@router.callback_query(F.data == "qa_menu")
async def qa_menu_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    language = user_languages.get(user_id, "en")

    text = "❓ Fragen & Antworten\n\nWählen Sie ein Thema:" if language == "de" else "❓ Q&A\n\nChoose a topic:"
    keyboard = get_quick_response_keyboard(language)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("qa_"))
async def qa_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    language = user_languages.get(user_id, "en")
    topic = callback.data.replace("qa_", "")
    
    # Map topics to search terms
    topic_map = {
        "hours": "opening hours",
        "facilities": "facilities",
        "cafe": "café",
        "safety": "safety",
        "vegetarian": "vegetarian"
    }
    
    if topic in topic_map:
        response = get_enhanced_response(topic_map[topic], str(user_id))
        keyboard = get_quick_response_keyboard(language)
        await callback.message.edit_text(response, reply_markup=keyboard)
    
    await callback.answer()

@router.callback_query(F.data.startswith("booking_") | F.data.startswith("entry_") | F.data.startswith("date_") | F.data.startswith("time_"))
async def booking_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    if user_id in user_languages:
        language = user_languages[user_id]
        if user_id not in booking_feature.booking_sessions:
            booking_feature.booking_sessions[user_id] = {}
        booking_feature.booking_sessions[user_id]["language"] = language
    else:
        user_languages[user_id] = "en"
        booking_feature.booking_sessions[user_id] = {"language": "en"}
    
    logger.info(f"Processing booking callback: {callback.data} from user {user_id}")
    
    try:
        await booking_feature.handle_booking_callback(callback, bot)
    except Exception as e:
        logger.error(f"Error in booking callback handler: {e}")
        error_text = "❌ Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut." if user_languages.get(user_id) == "de" else "❌ An error occurred. Please try again."
        await callback.message.edit_text(error_text)
        await callback.answer()
        
@router.callback_query(F.data == "accessibility_menu")
async def accessibility_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    language = user_languages.get(user_id, "en")

    text = accessibility_feature.get_info_text(language)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🔙 Zurück" if language == "de" else "🔙 Back",
            callback_data="main_menu"
        )]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


#TODO
@router.callback_query(F.data.startswith("navigation_"))
async def navigation_callback(callback: types.CallbackQuery):
    await callback.message.answer("On the way")

@router.callback_query(F.data == "contact_info")
async def contact_info_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    language = user_languages.get(user_id, "en")
    
    if language == "de":
        contact_text=contact_text_de
    else:
        contact_text=contact_text_en

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🔙 Zurück" if language == "de" else "🔙 Back", 
            callback_data="main_menu"
        )]
    ])
    
    await callback.message.edit_text(contact_text, reply_markup=keyboard)
    await callback.answer()

# unhandled callbacks
@router.callback_query()
async def handle_unhandled_callback(callback: types.CallbackQuery):
    logger.warning(f"Unhandled callback query: {callback.data} from user {callback.from_user.id}")
    await callback.answer("This function is not yet implemented.")

@router.message(F.text)
async def handle_text_message(message: types.Message):
    """Handle text messages"""
    user_id = message.from_user.id
    text = message.text.lower()
    
    language = detect_language(message.text)
    user_languages[user_id] = language
    
    booking_keywords = [
        "book", "booking", "reserve", "reservation", "ticket", 
        "buchen", "buchung", "reservierung", "ticket", "eintrittskarte"
    ]
    
    accessibility_keywords = [
        "accessibility", "disabled", "wheelchair", "barrierefreiheit", 
        "behindert", "rollstuhl", "autism", "autismus", "sensory", "sensorisch"
    ]

    if any(keyword in text for keyword in booking_keywords):
        await booking_feature.handle_text_booking(message, bot)
    elif any(keyword in text for keyword in accessibility_keywords):
        response = accessibility_feature.get_info_text(language)
        keyboard = get_main_menu_keyboard(language)
        await message.answer(response, reply_markup=keyboard)
    else:
        response = get_enhanced_response(message.text, str(user_id))
        keyboard = get_main_menu_keyboard(language)
        await message.answer(response, reply_markup=keyboard)
    
@router.message(F.voice)
async def handle_voice_message(message: types.Message):
    user_id = message.from_user.id
    language = user_languages.get(user_id, "en")

    if voice_processor is None:
        if language == "de":
            response = voice_response_de
        else:
            response = voice_response_en
        
        keyboard = get_main_menu_keyboard(language)
        await message.answer(response, reply_markup=keyboard)
        return
    
    try:
        processing_msg = "🎤 Verarbeite Sprachnachricht..." if language == "de" else "🎤 Processing voice message..."
        status_message = await message.answer(processing_msg)
        
        # downloaded voice file
        file_info = await bot.get_file(message.voice.file_id)
        voice_file = await bot.download_file(file_info.file_path)
        
        # transcribe
        transcribed_text, detected_lang = await voice_processor.transcribe_voice(voice_file.getvalue())
        
        if transcribed_text:
            user_languages[user_id] = detected_lang
            
            await status_message.delete()
            
            transcript_msg = f"🗣️ {transcribed_text}" if detected_lang == "de" else f"🗣️ {transcribed_text}"
            await message.answer(transcript_msg, parse_mode="Markdown")
            
            await process_transcribed_text(message, transcribed_text, detected_lang)
        else:
            error_msg = "❌ Spracherkennung fehlgeschlagen" if language == "de" else "❌ Voice recognition failed"
            await status_message.edit_text(error_msg)
            
    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        error_msg = "❌ Fehler bei der Sprachverarbeitung" if language == "de" else "❌ Voice processing error"
        
        try:
            await status_message.edit_text(error_msg)
        except:
            await message.answer(error_msg)


async def process_transcribed_text(message: types.Message, text: str, language: str):
    user_id = message.from_user.id
    text_lower = text.lower()

    if not text or not isinstance(text, str):
        logger.warning(f"Invalid transcribed text: {text}")
        return
    
    booking_keywords = [
        "book", "booking", "reserve", "reservation", "ticket", 
        "buchen", "buchung", "reservierung", "ticket", "eintrittskarte"
    ]
    
    accessibility_keywords = [
        "accessibility", "disabled", "wheelchair", "barrierefreiheit", 
        "behindert", "rollstuhl", "autism", "autismus", "sensory", "sensorisch"
    ]

    try:
        if any(keyword in text_lower for keyword in booking_keywords):
            # Create a new message-like object instead of modifying the frozen one
            class TextMessage:
                def __init__(self, original_message, text):
                    self.text = text
                    self.from_user = original_message.from_user
                    self.chat = original_message.chat
                    self.reply = original_message.reply
                    self.answer = original_message.answer
            
            text_message = TextMessage(message, text)
            await booking_feature.handle_text_booking(text_message, bot)
        elif any(keyword in text_lower for keyword in accessibility_keywords):
            response = accessibility_feature.get_info_text(language)
            keyboard = get_main_menu_keyboard(language)
            await message.answer(response, reply_markup=keyboard)
        else:
            response = get_enhanced_response(text, str(user_id))
            keyboard = get_main_menu_keyboard(language)
            await message.answer(response, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error processing transcribed text: {e}")
        error_msg = "❌ Fehler bei der Textverarbeitung" if language == "de" else "❌ Error processing text"
        await message.answer(error_msg)

#TODO
@router.message(F.location)
async def handle_location(message: types.Message):
    """Handle location sharing"""
    user_id = message.from_user.id
    language = user_languages.get(user_id, "en")
    
    lat = message.location.latitude
    lon = message.location.longitude
    
    if language == "de":
        response=location_response_de
    else:
        response=location_response_en

    keyboard = get_main_menu_keyboard(language)
    await message.answer(response, reply_markup=keyboard)

#TODO
@router.message(F.photo)
async def handle_photo(message: types.Message):
    pass

async def main():
    logger.info("Starting Bamboolino Playground Bot...")
    
    dp.include_router(router)
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")