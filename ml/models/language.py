import re
import logging
from typing import Dict, Any, Tuple, List
from ml.data.preprocessing import TextPreprocessor

logger = logging.getLogger("sif_ml")

# Configurable Multilingual Domain Safety Vocabulary (English, Hindi, Tamil)
MULTILINGUAL_SAFETY_VOCABULARY = {
    "CONFINED_SPACE": {
        "en": ["confined space", "tank entry", "vessel entry", "manhole", "gas test"],
        "hi": ["बंद स्थान", "टैंक प्रवेश", "गैस परीक्षण"],
        "ta": ["குறுகிய இடம்", "தொட்டி நுழைவு", "கேஸ் பரிசோதனை"],
    },
    "WORKING_AT_HEIGHT": {
        "en": ["scaffolding", "harness", "height", "ladder", "fall arrest"],
        "hi": ["ऊंचाई पर कार्य", "मचान", "सुरक्षा बेल्ट"],
        "ta": ["உயரத்தில் வேலை", "சாரக்கட்டு", "பாதுகாப்பு பெல்ட்"],
    },
    "HOT_WORK": {
        "en": ["welding", "cutting", "grinding", "sparks", "hot work"],
        "hi": ["वेल्डिंग", "कटिंग", "हॉट वर्क", "चिंगारी"],
        "ta": ["வெல்டிங்", "கட்டிங்", "ஹாட் வொர்க்"],
    },
    "ELECTRICAL_SAFETY": {
        "en": ["loto", "live wire", "high voltage", "short circuit", "substation"],
        "hi": ["बिजली का झटका", "हाई वोल्टेज", "लाइव वायर"],
        "ta": ["மின்சாரம்", "உயர் மின்னழுத்தம்", "லைவ் வயர்"],
    }
}


class MultilingualSafetyEngine:
    """
    Multilingual Safety Terminology Mapper and Language Detector.
    """

    @staticmethod
    def process_multilingual_report(text: str) -> Dict[str, Any]:
        """
        Detects language and extracts multilingual safety terminology.
        """
        lang_code, confidence = TextPreprocessor.detect_language(text)

        detected_terms: List[str] = []
        matched_category = "GENERAL_SAFETY"

        text_lower = text.lower()
        for cat, lang_dict in MULTILINGUAL_SAFETY_VOCABULARY.items():
            for lang, keywords in lang_dict.items():
                for kw in keywords:
                    if kw in text_lower:
                        detected_terms.append(f"{kw} ({lang})")
                        matched_category = cat

        return {
            "language": lang_code,
            "language_name": "Hindi" if lang_code == "hi" else ("Tamil" if lang_code == "ta" else "English"),
            "language_confidence": confidence,
            "detected_multilingual_terms": detected_terms,
            "matched_category": matched_category,
        }
