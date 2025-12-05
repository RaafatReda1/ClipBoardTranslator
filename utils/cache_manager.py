"""
Cache Manager for MedTranslate Pro
Caches translation results for faster repeated lookups
"""

from cachetools import LRUCache
from typing import Optional, Tuple
import hashlib


class CacheManager:
    """Manages translation caching"""
    
    def __init__(self, max_size: int = 100):
        """Initialize cache with maximum size"""
        self.cache = LRUCache(maxsize=max_size)
    
    def _generate_key(self, text: str, source: str, source_lang: str, target_lang: str) -> str:
        """Generate unique cache key"""
        key_string = f"{text}|{source}|{source_lang}|{target_lang}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, text: str, source: str, source_lang: str = "auto", 
            target_lang: str = "ar") -> Optional[str]:
        """Get cached translation"""
        key = self._generate_key(text, source, source_lang, target_lang)
        return self.cache.get(key)
    
    def set(self, text: str, translation: str, source: str, 
            source_lang: str = "auto", target_lang: str = "ar"):
        """Cache translation result"""
        key = self._generate_key(text, source, source_lang, target_lang)
        self.cache[key] = translation
    
    def clear(self):
        """Clear all cached translations"""
        self.cache.clear()
    
    def get_stats(self) -> Tuple[int, int]:
        """Get cache statistics (current_size, max_size)"""
        return len(self.cache), self.cache.maxsize
