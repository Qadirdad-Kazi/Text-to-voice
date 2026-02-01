"""
Text Normalization Module
Offline-only normalization for English, Urdu, and Sindhi
"""

import re
from typing import Dict

class TextNormalizer:
    """
    Normalize input text for phoneme-based synthesis.
    Keeps punctuation for pause modeling.
    """

    PUNCTUATION_MAP: Dict[str, str] = {
        "۔": ".",
        "؟": "?",
        "،": ",",
        "؛": ";",
        "!": "!",
        "?": "?",
        ".": ".",
        ",": ",",
        ";": ";",
        ":": ":",
    }

    def normalize(self, text: str, language: str = "English") -> str:
        if not text:
            return ""

        # Normalize whitespace
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[\t ]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Normalize punctuation symbols
        normalized_chars = []
        for ch in text:
            normalized_chars.append(self.PUNCTUATION_MAP.get(ch, ch))

        normalized = "".join(normalized_chars)

        # Trim surrounding whitespace
        normalized = normalized.strip()

        # Lowercase English for stable mapping
        if language.lower() == "english":
            normalized = normalized.lower()

        return normalized
