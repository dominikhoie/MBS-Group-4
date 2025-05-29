import re
from typing import Dict, List, Tuple, Optional

QA_DATABASE = {
    "opening_hours": {
        "en": "🕘 Bamboolino Playground is open:\n📅 Monday to Friday: 9:00-18:00\n📅 Saturday to Sunday: 8:00-20:00",
        "de": "🕘 Bamboolino Spielplatz ist geöffnet:\n📅 Montag bis Freitag: 9:00-18:00\n📅 Samstag bis Sonntag: 8:00-20:00",
        "keywords": ["opening hours", "business hours", "öffnungszeiten", "geschäftszeiten", "open", "geöffnet"]
    },
    
    "facilities": {
        "en": "🎢 We offer exciting facilities:\n• 🛝 Slides and climbing frames\n• 🎠 Swings and roundabouts\n• 🏖️ Sand pits\n• 🏠 Indoor play area\n• 🎯 Suitable for children aged 2–12",
        "de": "🎢 Wir bieten aufregende Einrichtungen:\n• 🛝 Rutschen und Klettergerüste\n• 🎠 Schaukeln und Karussells\n• 🏖️ Sandkästen\n• 🏠 Innenspielbereich\n• 🎯 Geeignet für Kinder von 2–12 Jahren",
        "keywords": ["facilities", "equipment", "playground", "einrichtungen", "spielgeräte", "spielplatz", "slides", "swings", "rutschen", "schaukeln"]
    },
    
    "cafe": {
        "en": "☕ Our café offers:\n• ☕ Coffee, tea, and fresh juices\n• 🍰 Delicious cakes and pastries\n• 🥪 Fresh sandwiches\n• 🕘 Open during playground hours",
        "de": "☕ Unser Café bietet:\n• ☕ Kaffee, Tee und frische Säfte\n• 🍰 Leckere Kuchen und Gebäck\n• 🥪 Frische Sandwiches\n• 🕘 Geöffnet während der Spielplatz-Öffnungszeiten",
        "keywords": ["café", "cafe", "coffee", "food", "drinks", "kaffee", "essen", "getränke", "restaurant"]
    },
    
    "vegetarian": {
        "en": "🥗 Vegetarian Options:\n• 🥪 Vegetarian sandwiches\n• 🥗 Fresh salads\n• 🍰 Vegetarian cakes\n• 🌱 Vegan options available\n📞 Please inform us of dietary needs in advance!",
        "de": "🥗 Vegetarische Optionen:\n• 🥪 Vegetarische Sandwiches\n• 🥗 Frische Salate\n• 🍰 Vegetarische Kuchen\n• 🌱 Vegane Optionen verfügbar\n📞 Bitte teilen Sie uns Ihre Ernährungsbedürfnisse im Voraus mit!",
        "keywords": ["vegetarian", "vegan", "menu", "vegetarisch", "vegan", "speisekarte", "dietary", "ernährung"]
    },
    
    "safety": {
        "en": "🛡️ Safety First:\n• ✅ All equipment meets international safety standards\n• 🔍 Weekly safety inspections\n• 👨‍🔧 Professional maintenance team\n• 📋 Certified safety protocols",
        "de": "🛡️ Sicherheit zuerst:\n• ✅ Alle Geräte entsprechen internationalen Sicherheitsstandards\n• 🔍 Wöchentliche Sicherheitsinspektionen\n• 👨‍🔧 Professionelles Wartungsteam\n• 📋 Zertifizierte Sicherheitsprotokolle",
        "keywords": ["safety", "equipment safety", "sicherheit", "gerätesicherheit", "safe", "sicher", "inspection", "inspektion"]
    },
    
    # Accessibility features
    "accessibility": {
        "en": "♿ Accessibility Features:\n• 🚪 Wheelchair-accessible entrances\n• 🎢 Adapted playground equipment\n• 🔇 Sensory-friendly quiet zones\n• 🗺️ Visual accessibility guides\n• 🚻 Accessible restrooms\n• 🅿️ Disabled parking spaces",
        "de": "♿ Barrierefreiheit:\n• 🚪 Rollstuhlgerechte Eingänge\n• 🎢 Angepasste Spielgeräte\n• 🔇 Sensorfreundliche ruhige Bereiche\n• 🗺️ Visuelle Barrierefreiheits-Leitfäden\n• 🚻 Barrierefreie Toiletten\n• 🅿️ Behindertenparkplätze",
        "keywords": ["accessibility", "disabled", "wheelchair", "barrierefreiheit", "behindert", "rollstuhl", "accessible", "barrierefrei"]
    },
    
    "wheelchair_access": {
        "en": "♿ Wheelchair Access:\n• 🚪 3 wheelchair-accessible entrances\n• 🛤️ Smooth pathways throughout the facility\n• 🎢 Ground-level play equipment\n• 🎯 Easy-reach activity stations\n• 🚻 Fully accessible restrooms",
        "de": "♿ Rollstuhlzugang:\n• 🚪 3 rollstuhlgerechte Eingänge\n• 🛤️ Glatte Wege durch die gesamte Anlage\n• 🎢 Ebenerdige Spielgeräte\n• 🎯 Leicht erreichbare Aktivitätsstationen\n• 🚻 Vollständig barrierefreie Toiletten",
        "keywords": ["wheelchair", "rollstuhl", "access", "zugang", "entrance", "eingang", "pathway", "weg"]
    },
    
    "sensory_friendly": {
        "en": "🔇 Sensory-Friendly Zones:\n• 🤫 Quiet areas with reduced noise\n• 💡 Adjustable lighting\n• 🎨 Calming sensory activities\n• 🕰️ Designated quiet hours: 9-11 AM\n• 👂 Noise-canceling headphones available",
        "de": "🔇 Sensorfreundliche Bereiche:\n• 🤫 Ruhige Bereiche mit reduziertem Lärm\n• 💡 Anpassbare Beleuchtung\n• 🎨 Beruhigende sensorische Aktivitäten\n• 🕰️ Festgelegte ruhige Stunden: 9-11 Uhr\n• 👂 Geräuschunterdrückende Kopfhörer verfügbar",
        "keywords": ["sensory", "quiet", "noise", "sensorisch", "ruhig", "lärm", "autism", "autismus", "sensitive", "empfindlich"]
    }
}

# Context memory for conversations
user_context = {}

def detect_language(text: str) -> str:
    german_words = ["ich", "und", "der", "die", "das", "ist", "haben", "mit", "für", "auf", "zu", "öffnungszeiten", "spielplatz", "kaffee"]
    english_words = ["the", "and", "is", "are", "have", "with", "for", "opening", "hours", "playground", "coffee"]
    
    text_lower = text.lower()
    german_count = sum(1 for word in german_words if word in text_lower)
    english_count = sum(1 for word in english_words if word in text_lower)
    
    return "de" if german_count > english_count else "en"

def find_best_match(user_text: str) -> Tuple[Optional[str], int]:
    user_text_lower = user_text.lower()
    best_match = None
    best_score = 0
    
    for key, data in QA_DATABASE.items():
        score = 0
        for keyword in data["keywords"]:
            if keyword.lower() in user_text_lower:
                score += 1
        
        if score > best_score:
            best_score = score
            best_match = key
    
    return best_match, best_score

def get_enhanced_response(user_text: str, user_id: str = "default") -> str:
    
    language = detect_language(user_text)
    
    if user_id not in user_context:
        user_context[user_id] = {"language": language, "conversation_count": 0}
    else:
        user_context[user_id]["language"] = language
    
    user_context[user_id]["conversation_count"] += 1
    
    best_match, score = find_best_match(user_text)
    
    if best_match and score > 0:
        response_data = QA_DATABASE[best_match]
        response = response_data[language]
        
        if user_context[user_id]["conversation_count"] > 1:
            greeting = "Welcome back! 👋" if language == "en" else "Willkommen zurück! 👋"
            response = f"{greeting}\n\n{response}"
        
        return response
    
    fallback_responses = {
        "en": "🤔 I didn't quite understand your question.\n\n💬 I can help you with:\n• 🕘 Opening hours\n• 🎢 Facilities and equipment\n• ☕ Café and food options\n• ♿ Accessibility features\n• 🛡️ Safety information\n\n✨ Try asking: 'What are your opening hours?' or 'Do you have wheelchair access?'",
        "de": "🤔 Ich habe Ihre Frage nicht ganz verstanden.\n\n💬 Ich kann Ihnen helfen mit:\n• 🕘 Öffnungszeiten\n• 🎢 Einrichtungen und Geräte\n• ☕ Café und Speiseoptionen\n• ♿ Barrierefreiheit\n• 🛡️ Sicherheitsinformationen\n\n✨ Versuchen Sie zu fragen: 'Wie sind Ihre Öffnungszeiten?' oder 'Haben Sie Rollstuhlzugang?'"
    }
    
    return fallback_responses[language]

def get_accessibility_info(query: str, language: str = "en") -> str:
    """Specific function for accessibility-related queries"""
    
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["wheelchair", "rollstuhl"]):
        return QA_DATABASE["wheelchair_access"][language]
    elif any(word in query_lower for word in ["sensory", "quiet", "noise", "autism", "sensorisch", "ruhig", "autismus"]):
        return QA_DATABASE["sensory_friendly"][language]
    else:
        return QA_DATABASE["accessibility"][language]