"""
NLP preprocessing for the Context-Aware Smart Communication Assistant.

Designed for low-resource regional-language and code-mixed input.
The pipeline is intentionally lightweight so it can run on a student laptop.
"""

import re
import unicodedata
from typing import List

# Small project-specific stop-word lists.  They are deliberately conservative:
# removing too many regional words can destroy intent information.
STOP_WORDS = {
    "en": {"the", "a", "an", "is", "are", "am", "to", "of", "in", "on", "for"},
    "kn": {"ಅದು", "ಇದು", "ಮತ್ತು", "ಒಂದು"},
    "tcy": {"and", "the", "a", "an"},
    "kok": {"ani", "ek", "tem"},
}

def normalize_unicode(text: str) -> str:
    text = unicodedata.normalize("NFC", text or "")
    return text.strip()

def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def tokenize(text: str) -> List[str]:
    """
    Unicode-aware tokenizer for English and regional Indian languages.

    Preserves combining marks used by Kannada and other Indic scripts
    while removing punctuation and symbols.
    """
    tokens = []

    for raw_token in text.split():
        cleaned = "".join(
            ch for ch in raw_token
            if not unicodedata.category(ch).startswith(("P", "S"))
        )

        if cleaned:
            tokens.append(cleaned)

    return tokens
def preprocess_text(text: str, language: str = "en") -> str:
    """
    Normalize input before TF-IDF inference.
    For regional scripts, preserve Unicode characters and avoid aggressive
    stemming/lemmatization because high-quality stemmers are unavailable.
    """
    text = normalize_unicode(text)
    text = normalize_whitespace(text)
    if not text:
        return ""

    # Lowercase only affects scripts where case exists; Kannada/Tulu/Konkani
    # Unicode text remains unchanged.
    text = text.lower()
    tokens = tokenize(text)

    lang = (language or "en").lower()[:3]
    stop_words = STOP_WORDS.get(lang, set())
    tokens = [tok for tok in tokens if tok not in stop_words]

    return " ".join(tokens)

def detect_code_mixing(text: str) -> bool:
    """
    Lightweight heuristic: identifies inputs containing both Latin and
    non-Latin scripts. This is useful for Kannada/English-style code-mixing.
    """
    has_latin = bool(re.search(r"[A-Za-z]", text or ""))
    has_non_latin = bool(re.search(r"[^\x00-\x7F]", text or ""))
    return has_latin and has_non_latin
