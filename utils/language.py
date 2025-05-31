import re
from typing import Dict, Tuple, Union

def detect_language(text: str, return_confidence: bool = False) -> Union[str, Tuple[str, float]]:
    if not text or len(text.strip()) < 2:
        result = "en"
        return (result, 1.0) if return_confidence else result
    
    text_lower = text.lower().strip()
    
    german_high = {"der", "die", "das", "und", "ich", "ist", "mit", "für", "haben", "öffnungszeiten", 
                   "spielplatz", "barrierefreiheit", "rollstuhl", "geöffnet", "sicherheit"}
    english_high = {"the", "and", "are", "you", "what", "how", "opening", "hours", "playground", 
                    "accessibility", "wheelchair", "facilities", "safety"}
    
    german_med = {"zu", "auf", "von", "eine", "ein", "kann", "wird", "kaffee", "vegetarisch", 
                  "einrichtungen", "geschäft"}
    english_med = {"is", "have", "with", "that", "this", "can", "will", "coffee", "vegetarian", 
                   "business", "equipment"}
    
    words = re.findall(r'\b\w+\b', text_lower)
    
    #calculate the score
    german_score = 0
    english_score = 0
    
    for word in words:
        if word in german_high:
            german_score += 3
        elif word in german_med:
            german_score += 1
        elif word in english_high:
            english_score += 3
        elif word in english_med:
            english_score += 1
    
    # language pattern
    if re.search(r'[üöäß]', text_lower):
        german_score += 2
    if re.search(r'\w+(heit|keit|ung)\b', text_lower):
        german_score += 1
    if re.search(r'\bsch\w+', text_lower):
        german_score += 1
    
    if re.search(r'\b\w+ing\b', text_lower):
        english_score += 1
    if re.search(r'\b\w+(tion|ly)\b', text_lower):
        english_score += 1
    
    if german_score == english_score == 0:
        result = "de" if re.search(r'[üöäß]', text_lower) else "en"
        confidence = 0.5
    else:
        result = "de" if german_score > english_score else "en"
        total = german_score + english_score
        confidence = max(german_score, english_score) / total if total > 0 else 0.5
    
    return (result, confidence) if return_confidence else result


def detect_language_batch(texts: list) -> Dict[str, str]:
    return {text: detect_language(text) for text in texts}


def get_language_info(text: str) -> Dict[str, any]:
    language, confidence = detect_language(text, return_confidence=True)
    
    return {
        "language": language,
        "confidence": confidence,
        "is_confident": confidence > 0.7,
        "text_length": len(text.strip()),
        "word_count": len(re.findall(r'\b\w+\b', text))
    }
