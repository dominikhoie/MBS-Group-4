# features/accessibility/accessibility_feature.py

from utils.text_messages import accessibility_text_de, accessibility_text_en

class AccessibilityFeature:
    def get_info_text(self, language: str) -> str:
        if language == "de":
            return accessibility_text_de
        else:
            return accessibility_text_en
