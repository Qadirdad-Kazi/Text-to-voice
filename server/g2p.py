"""
Grapheme-to-Phoneme (G2P) Converter
Offline-only, rule-based mapping for phoneme tokens
"""

from typing import Dict, List

class G2PConverter:
    """
    Convert normalized text into phoneme tokens.
    This is rule-based and uses provided phoneme maps.
    """

    def __init__(self, pause_tokens: Dict[str, int]):
        self.pause_tokens = pause_tokens

    def to_tokens(self, text: str, phoneme_map: Dict[str, Dict]) -> List[str]:
        tokens: List[str] = []
        for ch in text:
            if ch in phoneme_map or ch in self.pause_tokens or ch == "\n":
                tokens.append(ch)
            else:
                # Unknown character -> short pause marker
                tokens.append("<UNK>")
        return tokens
