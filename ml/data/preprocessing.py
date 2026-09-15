import re
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger("sif_ml")

# Negation terms that must be preserved semantically
NEGATION_WORDS = {
    "without", "no", "not", "failed", "failure", "missing", "absent",
    "never", "didnt", "did not", "unable", "lack", "lacking", "bypassed", "override"
}

# Domain safety keywords across categories
SAFETY_KEYWORDS = {
    "confined_space": ["confined space", "vessel entry", "tank entry", "manhole", "gas test", "oxygen deficiency", "h2s", "nitrogen purging"],
    "working_at_height": ["scaffolding", "harness", "safety belt", "height", "ladder", "fall arrest", "roof work", "open edge", "elevated"],
    "electrical_safety": ["loto", "lockout", "tagout", "live wire", "high voltage", "arc flash", "substation", "electrical panel"],
    "hot_work": ["welding", "cutting", "grinding", "spark", "hot work permit", "fire watch", "ignition"],
    "lifting": ["crane", "hoist", "suspended load", "rigging", "sling", "lifting beam"],
    "pressure_systems": ["pipeline", "pressure", "relief valve", "wellhead", "booster pump", "flange leak", "blowout"],
}


class TextPreprocessor:
    """
    NLP Text Preprocessing Engine with Negation-Aware Semantic Preservation
    and Language Identification.
    """

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Cleans and normalizes report text while preserving negation words and domain terms.
        """
        if not text:
            return ""

        # Normalize whitespace
        cleaned = re.sub(r"\s+", " ", str(text).strip())

        # Convert to lowercase for NLP matching
        cleaned_lower = cleaned.lower()

        # Remove special noise characters but preserve hyphens, commas, periods
        cleaned_clean = re.sub(r"[^\w\s\-\.,]", " ", cleaned_lower)
        cleaned_final = re.sub(r"\s+", " ", cleaned_clean).strip()

        return cleaned_final

    @staticmethod
    def detect_language(text: str) -> Tuple[str, float]:
        """
        Detects language of input text (English, Hindi, Tamil) returning (lang_code, confidence).
        """
        if not text or not text.strip():
            return "en", 1.0

        # Check unicode ranges for Devanagari (Hindi) and Tamil script
        hindi_chars = len(re.findall(r"[\u0900-\u097F]", text))
        tamil_chars = len(re.findall(r"[\u0B80-\u0BFF]", text))
        total_chars = len(text)

        if hindi_chars > 0 and (hindi_chars / total_chars) > 0.15:
            return "hi", round(min(0.99, hindi_chars / total_chars + 0.5), 2)
        if tamil_chars > 0 and (tamil_chars / total_chars) > 0.15:
            return "ta", round(min(0.99, tamil_chars / total_chars + 0.5), 2)

        # Default to English
        return "en", 0.98

    @staticmethod
    def extract_negations_and_hazards(text: str) -> Dict[str, Any]:
        """
        Extracts negation phrases and hazard indicators from text.
        """
        text_lower = text.lower()
        words = set(re.findall(r"\b\w+\b", text_lower))
        detected_negations = list(words.intersection(NEGATION_WORDS))

        matched_categories = []
        for cat, kws in SAFETY_KEYWORDS.items():
            if any(kw in text_lower for kw in kws):
                matched_categories.append(cat.upper())

        return {
            "has_negation": len(detected_negations) > 0,
            "detected_negations": detected_negations,
            "matched_categories": matched_categories,
        }

    @staticmethod
    def analyze_safety_context(text: str) -> Dict[str, Any]:
        """
        Analyzes safety context, distinguishing UNSAFE_BEHAVIOR, SAFE_COMPLIANCE,
        PREVENTED_EVENT, and NEAR_MISS. Extracts real report evidence phrases.
        """
        if not text or not text.strip():
            return {
                "context_type": "UNKNOWN",
                "evidence_phrases": [],
                "compliance_detected": False,
                "prevention_detected": False,
                "unsafe_detected": False,
                "near_miss_detected": False
            }

        text_lower = text.lower()

        # Phrases indicating positive safety compliance
        compliance_phrases = [
            "completed gas testing", "gas testing completed", "gas testing was completed",
            "used required ppe", "wore ppe", "used ppe", "ppe was provided", "ppe was used",
            "fall protection used", "fall protection connected", "fall protection was used",
            "permit obtained", "permit was obtained", "permit approved", "authorization obtained",
            "isolation completed", "lockout completed", "energy isolated", "inspection completed"
        ]

        # Phrases indicating a prevented event / work stoppage before hazard exposure
        prevention_phrases = [
            "did not enter", "did not work", "work was stopped", "stopped work",
            "entry was prevented", "worker refused entry", "operation was halted",
            "prevented until", "work did not continue", "refused to enter", "did not start"
        ]

        # Phrases indicating unsafe act or condition
        unsafe_phrases = [
            "without gas testing", "without permit", "without ppe", "without fall protection",
            "without harness", "without safety harness", "without isolation", "entered without", "worked without",
            "bypassed", "overrode", "failed to", "no gas testing", "no ppe", "no permit",
            "unhooked", "unsecured", "exposed live"
        ]

        # Phrases indicating a near-miss event
        near_miss_phrases = [
            "nearly fell", "almost fell", "nearly struck", "almost hit",
            "gas alarm activated", "hydrocarbon leak", "flange leak", "wire snapped",
            "load shifted", "narrowly avoided"
        ]

        detected_compliance = [p for p in compliance_phrases if p in text_lower]
        detected_prevention = [p for p in prevention_phrases if p in text_lower]
        detected_unsafe = [p for p in unsafe_phrases if p in text_lower]
        detected_near_miss = [p for p in near_miss_phrases if p in text_lower]

        evidence_phrases = detected_compliance + detected_prevention + detected_unsafe + detected_near_miss

        # Decision hierarchy: Prevention > Compliance (if no unsafe action) > Near Miss > Unsafe Behavior > Unknown
        if detected_prevention and not detected_unsafe:
            context_type = "PREVENTED_EVENT"
        elif detected_compliance and not detected_unsafe:
            context_type = "SAFE_COMPLIANCE"
        elif detected_near_miss:
            context_type = "NEAR_MISS"
        elif detected_unsafe:
            context_type = "UNSAFE_BEHAVIOR"
        else:
            context_type = "UNKNOWN"

        return {
            "context_type": context_type,
            "evidence_phrases": list(set(evidence_phrases)),
            "compliance_detected": len(detected_compliance) > 0,
            "prevention_detected": len(detected_prevention) > 0,
            "unsafe_detected": len(detected_unsafe) > 0,
            "near_miss_detected": len(detected_near_miss) > 0
        }

