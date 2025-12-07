"""
Cache Manager for MedTranslate Pro
Caches translation results for faster repeated lookups
"""

from cachetools import LRUCache
from typing import Optional, Tuple
import hashlib


class CacheManager:
    """Manages translation caching"""
    
    def __init__(self, max_size: int = 100, persist_path: str = "resources/cache.json"):
        """Initialize cache with maximum size and persistence"""
        self.cache = LRUCache(maxsize=max_size)
        self.persist_path = persist_path
        self._load_from_disk()
    
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
        self._save_to_disk()
    
    def clear(self):
        """Clear all cached translations"""
        self.cache.clear()
        self._save_to_disk()
    
    def _load_from_disk(self):
        """Load cache from disk"""
        import json
        import os
        if os.path.exists(self.persist_path):
            try:
                with open(self.persist_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cache.update(data)
            except Exception as e:
                print(f"Error loading cache: {e}")
                
    def _save_to_disk(self):
        """Save cache to disk"""
        import json
        import os
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.persist_path), exist_ok=True)
            
        try:
            # LRUCache is dict-like, can be dumped directly
            with open(self.persist_path, 'w', encoding='utf-8') as f:
                json.dump(dict(self.cache), f, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving cache: {e}")

    def get_stats(self) -> Tuple[int, int]:
        """Get cache statistics (current_size, max_size)"""
        return len(self.cache), self.cache.maxsize
