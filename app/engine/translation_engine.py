"""
Gemini Translation Engine
Dịch text sử dụng Google Gemini API với context preservation
"""

import re
from typing import List, Dict, Optional, Tuple, Callable
from datetime import timedelta

try:
    import google.genai as genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    try:
        import genai
        GEMINI_AVAILABLE = True
    except ImportError:
        GEMINI_AVAILABLE = False

from app.models.subtitle import SubtitleFile, SubtitleEntry


# Supported target languages
LANGUAGES = {
    "en": "English",
    "vi": "Vietnamese",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ar": "Arabic",
    "hi": "Hindi",
    "th": "Thai",
    "id": "Indonesian",
    "ms": "Malay",
    "tl": "Tagalog",
    "nl": "Dutch",
    "pl": "Polish",
    "tr": "Turkish",
}


class TranslationCache:
    """Cache cho translated text."""

    def __init__(self):
        self._cache: Dict[str, str] = {}

    def get(self, source_text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Get cached translation."""
        key = self._make_key(source_text, source_lang, target_lang)
        return self._cache.get(key)

    def set(self, source_text: str, source_lang: str, target_lang: str, translated_text: str):
        """Set cache."""
        key = self._make_key(source_text, source_lang, target_lang)
        self._cache[key] = translated_text

    def clear(self):
        """Clear cache."""
        self._cache.clear()

    @staticmethod
    def _make_key(text: str, source_lang: str, target_lang: str) -> str:
        """Create cache key."""
        return f"{source_lang}:{target_lang}:{hash(text)}"


class GeminiTranslator:
    """
    Translation engine sử dụng Gemini API.
    Dịch toàn bộ SRT với context preservation.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or self._get_api_key()
        self.client = None
        self._initialized = False
        self.cache = TranslationCache()
        self._max_retries = 3

    def _get_api_key(self) -> str:
        """Get API key từ environment."""
        import os
        return os.environ.get("GEMINI_API_KEY", "")

    def initialize(self) -> bool:
        """Initialize Gemini client."""
        if not GEMINI_AVAILABLE:
            print("Warning: google-genai not installed")
            return False

        if not self.api_key:
            print("Warning: GEMINI_API_KEY not set")
            return False

        try:
            genai.configure(api_key=self.api_key)
            self._initialized = True
            return True
        except Exception as e:
            print(f"Failed to initialize Gemini: {e}")
            return False

    def translate_subtitle_file(
        self,
        sub_file: SubtitleFile,
        target_lang: str,
        progress_callback: Callable[[int, int], None] = None,
        batch_size: int = 50,
    ) -> Tuple[bool, str]:
        """
        Dịch toàn bộ subtitle file.
        Sử dụng context preservation để dịch chính xác hơn.
        """
        if not self._initialized:
            if not self.initialize():
                return False, "Failed to initialize Gemini"

        # Check cache first
        all_cached = True
        for entry in sub_file.entries:
            cached = self.cache.get(entry.text, sub_file.source_lang, target_lang)
            if cached:
                entry.translated_text = cached
            else:
                all_cached = False

        if all_cached:
            return True, "All entries from cache"

        # Process in batches
        for i in range(0, len(sub_file.entries), batch_size):
            batch = sub_file.entries[i : i + batch_size]
            success, error = self._translate_batch(
                batch, sub_file.source_lang, target_lang
            )
            if not success:
                return False, error

            if progress_callback:
                progress_callback(min(i + batch_size, len(sub_file.entries)), len(sub_file.entries))

        sub_file.target_lang = target_lang
        return True, "Translation complete"

    def _translate_batch(
        self,
        entries: List[SubtitleEntry],
        source_lang: str,
        target_lang: str,
    ) -> Tuple[bool, str]:
        """Dịch một batch entries."""
        # Prepare full context text
        context_text = "\n".join([e.text for e in entries])
        lang_name = LANGUAGES.get(target_lang, target_lang)

        # Build prompt với context preservation
        prompt = self._build_translation_prompt(
            context_text, source_lang, target_lang, lang_name
        )

        # Retry logic
        for attempt in range(self._max_retries):
            try:
                response = self._call_gemini(prompt)
                if response:
                    self._apply_translations(entries, response, source_lang, target_lang)
                    return True, ""
            except Exception as e:
                if attempt == self._max_retries - 1:
                    return False, str(e)

        return False, "Max retries exceeded"

    def _build_translation_prompt(
        self, text: str, source_lang: str, target_lang: str, lang_name: str
    ) -> str:
        """Build translation prompt cho Gemini."""
        return f"""You are a professional translator. Translate the following subtitles from {source_lang} to {lang_name}.

IMPORTANT RULES:
1. Preserve the exact meaning and tone of the original text
2. Keep colloquial expressions and slang in their natural equivalents
3. Maintain proper grammar in {lang_name}
4. Do NOT add explanations or notes
5. Keep each subtitle line SEPARATED by a double newline (\\n\\n)
6. Return ONLY the translated text, nothing else

ORIGINAL TEXT:
{text}

TRANSLATION:"""

    def _call_gemini(self, prompt: str) -> Optional[str]:
        """Call Gemini API."""
        if not GEMINI_AVAILABLE:
            return None

        try:
            response = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)
            return response.text if hasattr(response, "text") else str(response)
        except Exception as e:
            print(f"Gemini API error: {e}")
            return None

    def _apply_translations(
        self,
        entries: List[SubtitleEntry],
        translated_text: str,
        source_lang: str,
        target_lang: str,
    ):
        """Apply translations từ response cho các entries."""
        # Split by double newline
        lines = translated_text.strip().split("\n\n")

        for i, entry in enumerate(entries):
            if i < len(lines):
                translated = lines[i].strip()
                entry.translated_text = translated
                self.cache.set(entry.text, source_lang, target_lang, translated)

    def translate_single(
        self, text: str, source_lang: str, target_lang: str
    ) -> Optional[str]:
        """Dịch một đoạn text đơn lẻ."""
        # Check cache
        cached = self.cache.get(text, source_lang, target_lang)
        if cached:
            return cached

        if not self._initialized:
            if not self.initialize():
                return None

        lang_name = LANGUAGES.get(target_lang, target_lang)
        prompt = f"""Translate from {source_lang} to {lang_name}. Keep it natural and colloquial.

TEXT: {text}

TRANSLATION:"""

        for attempt in range(self._max_retries):
            try:
                response = self._call_gemini(prompt)
                if response:
                    translated = response.strip()
                    self.cache.set(text, source_lang, target_lang, translated)
                    return translated
            except Exception:
                if attempt == self._max_retries - 1:
                    return None

        return None

    def detect_language(self, text: str) -> str:
        """Detect language of text."""
        # Simple heuristics
        if any(c in text for c in "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"):
            return "vi"
        if any("\u4e00" <= c <= "\u9fff" for c in text):
            return "zh"
        if any(c in text for c in "ぁ-んァ-ン"):
            return "ja"
        if any("\uac00" <= c <= "\ud7af" for c in text):
            return "ko"
        if any("\u0600" <= c <= "\u06ff" for c in text):
            return "ar"
        return "en"