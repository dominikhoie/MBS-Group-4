from aiogram import Bot, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from datetime import datetime, timedelta
import json
import qrcode
import os
import logging
from utils.text_messages import booking_dashboard_de, booking_dashboard_en
from pathlib import Path

try:
    from utils.language import detect_language
except ImportError:
    def detect_language(text):
        return "en"
class BookingFeature:
    def __init__(self):
        self.booking_sessions = {}
        self.available_slots = {}

        self.booking_types = {
            "entry": {"en": "Entry Tickets", "de": "Eintrittskarten"},
            "gift": {"en": "Gift Vouchers", "de": "Gutscheine"},
            "restaurant": {"en": "Restaurant Reservation", "de": "Restaurantreservierung"},
            "birthday": {"en": "Birthday Party", "de": "Geburtstagsfeier"}
        }

        self.prices = {
            "entry": {"individual": 12, "family": 35, "group": 8},
            "gift": {"small": 25, "medium": 50, "large": 100},
            "restaurant": {"table": 0},
            "birthday": {"basic": 150, "premium": 250, "deluxe": 350}
        }

    def get_booking_keyboard(self, language: str = 'en') -> InlineKeyboardMarkup:
        """Create booking options keyboard"""
        if language == 'de':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎫 Eintrittskarten", callback_data="booking_entry")],
                [InlineKeyboardButton(text="🎁 Gutscheine", callback_data="booking_gift")],
                [InlineKeyboardButton(text="🍽️ Restaurantreservierung", callback_data="booking_restaurant")],
                [InlineKeyboardButton(text="🎂 Geburtstagsfeier", callback_data="booking_birthday")],
                [InlineKeyboardButton(text="🔙 Hauptmenü", callback_data="main_menu")]
            ])
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎫 Entry Tickets", callback_data="booking_entry")],
                [InlineKeyboardButton(text="🎁 Gift Vouchers", callback_data="booking_gift")],
                [InlineKeyboardButton(text="🍽️ Restaurant Reservation", callback_data="booking_restaurant")],
                [InlineKeyboardButton(text="🎂 Birthday Party", callback_data="booking_birthday")],
                [InlineKeyboardButton(text="🔙 Main Menu", callback_data="main_menu")]
            ])
        return keyboard
    
    def get_entry_ticket_keyboard(self, language: str = 'en') -> InlineKeyboardMarkup:
        """Create entry ticket options keyboard"""
        if language == 'de':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="👤 Einzelticket (€12)", callback_data="entry_individual")],
                [InlineKeyboardButton(text="👨‍👩‍👧‍👦 Familienticket (€35)", callback_data="entry_family")],
                [InlineKeyboardButton(text="👥 Gruppenticket (€8/Person)", callback_data="entry_group")],
                [InlineKeyboardButton(text="🔙 Zurück", callback_data="booking_main")]
            ])
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="👤 Individual Ticket (€12)", callback_data="entry_individual")],
                [InlineKeyboardButton(text="👨‍👩‍👧‍👦 Family Package (€35)", callback_data="entry_family")],
                [InlineKeyboardButton(text="👥 Group Ticket (€8/person)", callback_data="entry_group")],
                [InlineKeyboardButton(text="🔙 Back", callback_data="booking_main")]
            ])
        return keyboard

    def get_calendar_keyboard(self, language: str = 'en') -> InlineKeyboardMarkup:
        """Create date selection keyboard"""
        today = datetime.now()
        dates = []

        for i in range(7):
            date = today + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            display_date = date.strftime("%d.%m" if language == "de" else "%m/%d")
            day_name = date.strftime("%a")

            dates.append([
                InlineKeyboardButton(
                    text=f"{day_name} {display_date}",
                    callback_data=f'date_{date_str}'
                )
            ])

        dates.append([
            InlineKeyboardButton(
                text="🔙 Zurück" if language == "de" else "🔙 Back", 
                callback_data="booking_entry"
            )
        ])

        return InlineKeyboardMarkup(inline_keyboard=dates)

    def get_time_slots_keyboard(self, date: str, language: str = "en") -> InlineKeyboardMarkup:
        time_slots = [
            "09:00-12:00", "12:00-15:00", "15:00-18:00", "18:00-20:00"
        ]
        keyboard_rows = []

        for slot in time_slots:
            keyboard_rows.append([
                InlineKeyboardButton(
                    text=f"🕐 {slot}", 
                    callback_data=f"time_{date}_{slot}"
                )
            ])

        keyboard_rows.append([InlineKeyboardButton(
            text="🔙 Zurück" if language == "de" else "🔙 Back", 
            callback_data="select_date"
        )])

        return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    async def start_booking(self, message: types.Message, language: str = "en"):
        if language == 'de':
            text = booking_dashboard_de
        else:
            text = booking_dashboard_en
        
        keyboard = self.get_booking_keyboard(language)
        await message.reply(text, reply_markup=keyboard, parse_mode="Markdown")
        
    async def handle_booking_callback(self, callback_query: types.CallbackQuery, bot: Bot):
        data = callback_query.data
        user_id = str(callback_query.from_user.id)

        if user_id not in self.booking_sessions:
            self.booking_sessions[user_id] = {}

        language = self.booking_sessions[user_id].get("language", "en")

        try:
            if data == 'booking_main' or data == 'booking_menu':
                keyboard = self.get_booking_keyboard(language)
                text = "🎫 Buchungsoptionen" if language == "de" else "🎫 Booking Options"
                await callback_query.message.edit_text(text, reply_markup=keyboard)
            
            elif data == "booking_entry":
                self.booking_sessions[user_id]["type"] = "entry"
                self.booking_sessions[user_id]["language"] = language
                keyboard = self.get_entry_ticket_keyboard(language)
                text = "🎫 Eintrittskarten wählen:" if language == "de" else "🎫 Choose Entry Tickets:"
                await callback_query.message.edit_text(text, reply_markup=keyboard)
            
            elif data.startswith("entry_"):
                ticket_type = data.replace("entry_", "")
                self.booking_sessions[user_id]["subtype"] = ticket_type

                if ticket_type == "group":
                    text = "👥 Wie viele Personen? (Mindestens 10)" if language == "de" else "👥 How many people? (Minimum 10)"
                    await callback_query.message.edit_text(text)
                    self.booking_sessions[user_id]["waiting_for"] = "group_size"
                else:
                    keyboard = self.get_calendar_keyboard(language)
                    text = "📅 Datum wählen:" if language == "de" else "📅 Choose Date:"
                    await callback_query.message.edit_text(text, reply_markup=keyboard)

            elif data.startswith("date_"):
                date = data.replace("date_", "")
                self.booking_sessions[user_id]["date"] = date
                keyboard = self.get_time_slots_keyboard(date, language)
                text = f"🕐 Zeitslot für {date} wählen:" if language == "de" else f"🕐 Choose Time Slot for {date}:"
                await callback_query.message.edit_text(text, reply_markup=keyboard)

            elif data.startswith("time_"):
                parts = data.replace("time_", "").split("_")
                date = parts[0]
                time_slot = "_".join(parts[1:])
                self.booking_sessions[user_id]["time"] = time_slot
                
                # Generate booking confirmation
                await self.generate_booking_confirmation(callback_query, bot, user_id, language)
            
            elif data == "select_date":
                keyboard = self.get_calendar_keyboard(language)
                text = "📅 Datum wählen:" if language == "de" else "📅 Choose Date:"
                await callback_query.message.edit_text(text, reply_markup=keyboard)
            
            # Handle other booking types (simplified for now)
            elif data in ["booking_gift", "booking_restaurant", "booking_birthday"]:
                booking_type = data.replace("booking_", "")
                text = f"🚧 {self.booking_types[booking_type][language]} wird bald verfügbar sein!" if language == "de" else f"🚧 {self.booking_types[booking_type][language]} coming soon!"
                
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(
                        text="🔙 Zurück" if language == "de" else "🔙 Back", 
                        callback_data="booking_main"
                    )]
                ])
                await callback_query.message.edit_text(text, reply_markup=keyboard)

        except Exception as e:
            logging.error(f"Error in booking callback: {e}")
            error_text = "❌ Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut." if language == "de" else "❌ An error occurred. Please try again."
            await callback_query.message.edit_text(error_text)
        
        await callback_query.answer()

    async def handle_text_booking(self, message: types.Message, bot: Bot):
        user_id = str(message.from_user.id)
        text = message.text.lower()
        language = detect_language(message.text)
        
        if user_id in self.booking_sessions and "waiting_for" in self.booking_sessions[user_id]:
            if self.booking_sessions[user_id]["waiting_for"] == "group_size":
                try:
                    group_size = int(message.text)
                    if group_size < 10:
                        error_msg = "❌ Mindestens 10 Personen erforderlich" if language == "de" else "❌ Minimum 10 people required"
                        await message.reply(error_msg)
                        return
                    
                    self.booking_sessions[user_id]["group_size"] = group_size
                    del self.booking_sessions[user_id]["waiting_for"]
                    
                    keyboard = self.get_calendar_keyboard(language)
                    text = "📅 Datum wählen:" if language == "de" else "📅 Choose Date:"
                    await message.reply(text, reply_markup=keyboard)
                    
                except ValueError:
                    error_msg = "❌ Bitte geben Sie eine gültige Zahl ein" if language == "de" else "❌ Please enter a valid number"
                    await message.reply(error_msg)
                return
        
        booking_keywords = [
            "book", "booking", "reserve", "reservation", "ticket", "buchen", 
            "buchung", "reservierung", "ticket", "eintrittskarte"
        ]
        
        if any(keyword in text for keyword in booking_keywords):
            await self.start_booking(message, language)
    
    def generate_qr_code(self, booking_data: dict) -> str:
        try:
            booking_json = json.dumps(booking_data)
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(booking_json)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            qr_path = f"temp_qr_{booking_data['booking_id']}.png"
            img.save(qr_path)
            return qr_path
        except Exception as e:
            logging.error(f"Error generating QR code: {e}")
            return None
    
    async def generate_booking_confirmation(self, callback_query: types.CallbackQuery, bot: Bot, user_id: str, language: str):
        try:
            session = self.booking_sessions[user_id]
            
            booking_type = session.get("type", "entry")
            subtype = session.get("subtype", "individual")
            
            # Calculate price
            if booking_type == "entry":
                if subtype == "group":
                    price = self.prices["entry"]["group"] * session.get("group_size", 10)
                else:
                    price = self.prices["entry"][subtype]
            else:
                price = self.prices.get(booking_type, {}).get(subtype, 0)
            
            # Generate booking ID
            booking_id = f"BML{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            booking_data = {
                "booking_id": booking_id,
                "type": f"{booking_type}_{subtype}",
                "date": session.get("date"),
                "time": session.get("time"),
                "price": price,
                "user_id": user_id,
                "created_at": datetime.now().isoformat()
            }
            
            if language == "de":
                confirmation_text = f"""✅ **Buchung bestätigt!**

🎫 **Buchungsdetails:**
• Buchungs-ID: `{booking_id}`
• Typ: {booking_type.title()} - {subtype.title()}
• Datum: {session.get('date')}
• Zeit: {session.get('time')}
• Preis: €{price}

📱 Zeigen Sie diesen QR-Code am Eingang vor.
🎯 Ihre Buchung ist jetzt gesichert!"""
            else:
                confirmation_text = f"""✅ **Booking Confirmed!**

🎫 **Booking Details:**
• Booking ID: `{booking_id}`
• Type: {booking_type.title()} - {subtype.title()}
• Date: {session.get('date')}
• Time: {session.get('time')}
• Price: €{price}

📱 Show this QR code at the entrance.
🎯 Your booking is now secured!"""
            
            await callback_query.message.edit_text(confirmation_text, parse_mode="Markdown")
            
            qr_path = self.generate_qr_code(booking_data)
            if qr_path and os.path.exists(qr_path):
                try:
                    qr_file = FSInputFile(qr_path)
                    await bot.send_photo(callback_query.from_user.id, qr_file)
                except Exception as e:
                    logging.error(f"Error sending QR code: {e}")
                finally:
                    if os.path.exists(qr_path):
                        os.remove(qr_path)
            
            if user_id in self.booking_sessions:
                del self.booking_sessions[user_id]
                
        except Exception as e:
            logging.error(f"Error generating booking confirmation: {e}")
            error_text = "❌ Fehler bei der Buchungsbestätigung" if language == "de" else "❌ Error generating booking confirmation"
            await callback_query.message.edit_text(error_text)

booking_feature = BookingFeature()