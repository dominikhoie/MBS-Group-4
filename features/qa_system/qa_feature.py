# features/qa_system/qa_feature.py
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .qa_data import get_enhanced_response, get_accessibility_info
from utils.language import detect_language

class QAFeature:
    def __init__(self):
        pass
    
    def get_quick_response_keyboard(self, language: str = "en") -> InlineKeyboardMarkup:
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
    
    async def handle_qa_query(self, message: types.Message, language: str = "en") -> str:
        user_id = str(message.from_user.id)
        
        accessibility_keywords = [
            "accessibility", "disabled", "wheelchair", "barrierefreiheit", 
            "behindert", "rollstuhl", "autism", "autismus", "sensory", "sensorisch"
        ]
        
        if any(keyword in message.text.lower() for keyword in accessibility_keywords):
            return get_accessibility_info(message.text, language)
        else:
            return get_enhanced_response(message.text, user_id)