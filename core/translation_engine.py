"""
Translation Engine for MedTranslate Pro
Coordinates all translation sources and implements smart routing
"""

from typing import Optional, Tuple
import re
from .keyboard_fixer import KeyboardFixer
from .local_dictionary import LocalDictionary
from .libre_translator import LibreTranslator
from .openrouter_ai import OpenRouterAI
from utils.cache_manager import CacheManager
from utils.logger import Logger


class TranslationEngine:
    """Main translation engine coordinating all sources"""
    
    def __init__(self, config: dict, logger: Logger = None):
        """
        Initialize translation engine
        
        Args:
            config: Application configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger or Logger()
        
        # Initialize cache
        cache_size = config.get('translation', 'cache_size', default=100)
        self.cache = CacheManager(max_size=cache_size)
        
        # Initialize translation sources
        self.keyboard_fixer = KeyboardFixer()
        self.local_dict = LocalDictionary(
            config.get('dictionaries', 'medical_terms_path', default='dictionary.json')
        )
        self.libre_translator = LibreTranslator(
            timeout=config.get('advanced', 'network_timeout', default=5)
        )
        
        # Initialize OpenRouter AI
        ai_config = config.get('openrouter', default={})
        self.openrouter_ai = OpenRouterAI(
            api_key=ai_config.get('api_key', ''),
            model=ai_config.get('model', 'meta-llama/llama-3-8b-instruct:free'),
            system_prompt=ai_config.get('system_prompt', ''),
            custom_prompt=ai_config.get('custom_prompt', ''),
            max_tokens=ai_config.get('max_tokens', 150),
            temperature=ai_config.get('temperature', 0.7)
        )
        
        # Get active source and priority
        self.active_source = config.get('translation', 'active_source', default='auto')
        self.source_priority = config.get('translation', 'source_priority', 
                                         default=['keyboard_fixer', 'openrouter_ai', 'libre', 'local'])
        
        self.logger.info("Translation engine initialized")
    
    def translate(self, text: str, force_source: Optional[str] = None) -> Tuple[str, str]:
        """
        Translate text using appropriate source
        
        Args:
            text: Text to translate
            force_source: Force specific source (keyboard_fixer, local, libre, openrouter_ai)
        
        Returns:
            (translation, source_used)
        """
        if not text or len(text.strip()) == 0:
            return "Empty text", "none"
        
        # Validate input
        if not self._is_valid_input(text):
            return "Invalid input (too long or contains URLs)", "none"
        
        # Check cache first (if not forcing a source)
        if not force_source and self.config.get('translation', 'cache_enabled', default=True):
            cached = self.cache.get(text, self.active_source, "auto", "ar")
            if cached:
                self.logger.debug(f"Cache hit for: {text}")
                return cached, "cache"
        
        # Determine which source to use
        source = force_source or self.active_source
        
        if source == "auto":
            translation, source_used = self._auto_translate(text)
        else:
            translation, source_used = self._translate_with_source(text, source)
        
        # Cache successful translation
        if translation and translation != "Translation not found" and source_used != "cache":
            self.cache.set(text, translation, source_used, "auto", "ar")
        
        return translation, source_used
    
    def _auto_translate(self, text: str) -> Tuple[str, str]:
        """
        Automatically choose best translation source
        
        Returns:
            (translation, source_used)
        """
        # Follow priority order
        for source in self.source_priority:
            if source == "keyboard_fixer":
                # Check if it's a keyboard error
                is_fixed, fixed_text, fix_type = self.keyboard_fixer.detect_and_fix(text)
                if is_fixed:
                    self.logger.info(f"Keyboard fix: {text} → {fixed_text} ({fix_type})")
                    return f"Fixed: {fixed_text}", "keyboard_fixer"
            
            elif source == "local":
                # Try local dictionary
                translation = self.local_dict.translate(text)
                if translation:
                    self.logger.info(f"Local dict: {text} → {translation}")
                    return translation, "local"
            
            elif source == "libre":
                # Try LibreTranslate (if online)
                if self._is_network_available():
                    translation = self.libre_translator.translate(text, "auto", "ar")
                    if translation:
                        self.logger.info(f"LibreTranslate: {text} → {translation}")
                        return translation, "libre"
            
            elif source == "openrouter_ai":
                # Try OpenRouter AI (if online and looks like medical term)
                if self._is_network_available() and self._is_medical_term(text):
                    translation = self.openrouter_ai.translate(text)
                    if translation:
                        self.logger.info(f"OpenRouter AI: {text}")
                        return translation, "openrouter_ai"
        
        # Fallback to local dictionary if offline
        if self.config.get('translation', 'offline_fallback', default=True):
            translation = self.local_dict.translate(text)
            if translation:
                return translation, "local_fallback"
        
        return "Translation not found", "none"
    
    def _translate_with_source(self, text: str, source: str) -> Tuple[str, str]:
        """Translate using specific source"""
        try:
            if source == "keyboard_fixer":
                is_fixed, fixed_text, fix_type = self.keyboard_fixer.detect_and_fix(text)
                if is_fixed:
                    return f"Fixed ({fix_type}): {fixed_text}", "keyboard_fixer"
                else:
                    return "No keyboard error detected", "keyboard_fixer"
            
            elif source == "local":
                translation = self.local_dict.translate(text)
                return translation or "Not found in local dictionary", "local"
            
            elif source == "libre":
                translation = self.libre_translator.translate(text, "auto", "ar")
                return translation or "LibreTranslate unavailable", "libre"
            
            elif source == "openrouter_ai":
                translation = self.openrouter_ai.translate(text)
                return translation or "OpenRouter AI unavailable", "openrouter_ai"
            
            else:
                return f"Unknown source: {source}", "none"
        
        except Exception as e:
            self.logger.error(f"Translation error with {source}: {e}")
            return f"Error: {str(e)}", "error"
    
    def _is_valid_input(self, text: str) -> bool:
        """Validate input text"""
        # Check length
        if len(text) > 200:
            return False
        
        # Check for URLs
        url_pattern = r'http[s]?://|www\.|\.com|\.org|\.net'
        if re.search(url_pattern, text.lower()):
            return False
        
        return True
    
    def _is_medical_term(self, text: str) -> bool:
        """Simple heuristic to detect medical terms"""
        # Medical terms are usually:
        # - Single words or short phrases
        # - English letters
        # - Not too long
        words = text.split()
        if len(words) > 3:
            return False
        
        # Check if mostly English letters
        english_ratio = sum(1 for c in text if c.isascii() and c.isalpha()) / len(text)
        return english_ratio > 0.7
    
    def _is_network_available(self) -> bool:
        """Check if network is available"""
        # Simple check - try to reach LibreTranslate
        try:
            return self.libre_translator.is_available()
        except:
            return False
    
    def update_config(self, config: dict):
        """Update configuration"""
        self.config = config
        self.active_source = config.get('translation', 'active_source', default='auto')
        self.source_priority = config.get('translation', 'source_priority',
                                         default=['keyboard_fixer', 'openrouter_ai', 'libre', 'local'])
        
        # Update AI prompts
        ai_config = config.get('openrouter', default={})
        self.openrouter_ai.update_prompts(
            system_prompt=ai_config.get('system_prompt'),
            custom_prompt=ai_config.get('custom_prompt')
        )
    
    def get_stats(self) -> dict:
        """Get translation engine statistics"""
        cache_size, cache_max = self.cache.get_stats()
        dict_stats = self.local_dict.get_stats()
        
        return {
            "cache_size": cache_size,
            "cache_max": cache_max,
            "dictionary_entries": dict_stats.get("total_entries", 0),
            "active_source": self.active_source,
            "network_available": self._is_network_available()
        }
