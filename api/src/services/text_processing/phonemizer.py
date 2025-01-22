import re
import logging
import psutil
from abc import ABC, abstractmethod

import phonemizer

from .normalizer import normalize_text


class PhonemizerBackend(ABC):
    """Abstract base class for phonemization backends"""

    @abstractmethod
    def phonemize(self, text: str) -> str:
        """Convert text to phonemes

        Args:
            text: Text to convert to phonemes

        Returns:
            Phonemized text
        """
        pass


class EspeakBackend(PhonemizerBackend):
    """Espeak-based phonemizer implementation"""
    
    _instance = None
    
    def __new__(cls, language: str):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup(language)
        return cls._instance
        
    def _setup(self, language: str):
        """Initialize espeak backend

        Args:
            language: Language code ('en-us' or 'en-gb')
        """
        self.backend = phonemizer.backend.EspeakBackend(
            language=language, preserve_punctuation=True, with_stress=True
        )
        self.language = language

    def phonemize(self, text: str) -> str:
        """Convert text to phonemes using espeak

        Args:
            text: Text to convert to phonemes

        Returns:
            Phonemized text
            
        Raises:
            Exception: If phonemization fails, with detailed resource diagnostics
        """
        try:
        # Phonemize text
        ps = self.backend.phonemize([text])
        ps = ps[0] if ps else ""

        # Handle special cases
        ps = ps.replace("kəkˈoːɹoʊ", "kˈoʊkəɹoʊ").replace("kəkˈɔːɹəʊ", "kˈəʊkəɹəʊ")
        ps = ps.replace("ʲ", "j").replace("r", "ɹ").replace("x", "k").replace("ɬ", "l")
        ps = re.sub(r"(?<=[a-zɹː])(?=hˈʌndɹɪd)", " ", ps)
        ps = re.sub(r' z(?=[;:,.!?¡¿—…"«»"" ]|$)', "z", ps)

        # Language-specific rules
        if self.language == "en-us":
            ps = re.sub(r"(?<=nˈaɪn)ti(?!ː)", "di", ps)

            return ps.strip()
        except Exception as e:
            current_process = psutil.Process()
            logging.error(
                f"ESPEAK ERROR DIAGNOSTICS:\n"
                f"Open files: {current_process.open_files()}\n"
                f"Memory: {current_process.memory_info().rss/1024/1024}MB\n"
                f"Subprocesses: {current_process.children(recursive=True)}"
            )
            raise


def create_phonemizer(language: str = "a") -> PhonemizerBackend:
    """Factory function to create phonemizer backend

    Args:
        language: Language code ('a' for US English, 'b' for British English)

    Returns:
        Phonemizer backend instance
    """
    # Add periodic reset every 50 requests
    if not hasattr(create_phonemizer, "counter"):
        create_phonemizer.counter = 0
    create_phonemizer.counter += 1
    
    if create_phonemizer.counter % 50 == 0:
        if EspeakBackend._instance:
            EspeakBackend._instance.backend = None  # Force cleanup
            EspeakBackend._instance = None
    # Map language codes to espeak language codes
    lang_map = {"a": "en-us", "b": "en-gb"}

    if language not in lang_map:
        raise ValueError(f"Unsupported language code: {language}")

    return EspeakBackend(lang_map[language])


def phonemize(text: str, language: str = "a", normalize: bool = True) -> str:
    """Convert text to phonemes

    Args:
        text: Text to convert to phonemes
        language: Language code ('a' for US English, 'b' for British English)
        normalize: Whether to normalize text before phonemization

    Returns:
        Phonemized text
    """
    if normalize:
        text = normalize_text(text)

    phonemizer = create_phonemizer(language)
    return phonemizer.phonemize(text)
