"""
LibreTranslate Integration for MedTranslate Pro
Provides online translation using the translators library
"""

import translators as ts
from typing import Optional


class LibreTranslator:
    """Handles LibreTranslate API calls"""
    
    def __init__(self, timeout: int = 5):
        """Initialize LibreTranslate translator"""
        self.timeout = timeout
        self.translator_name = 'bing'  # Using Bing as it's more reliable than libre
    
    def translate(self, text: str, source_lang: str = 'auto', 
                  target_lang: str = 'ar') -> Optional[str]:
        """
        Translate text using LibreTranslate
        
        Args:
            text: Text to translate
            source_lang: Source language code ('auto' for auto-detect)
            target_lang: Target language code
        
        Returns:
            Translated text or None if error
        """
        try:
            # Use translators library (supports multiple backends)
            result = ts.translate_text(
                query_text=text,
                translator=self.translator_name,
                from_language=source_lang if source_lang != 'auto' else 'en',
                to_language=target_lang,
                timeout=self.timeout
            )
            return result
        except Exception as e:
            print(f"LibreTranslate error: {e}")
            # Try fallback translator
            try:
                result = ts.translate_text(
                    query_text=text,
                    translator='google',
                    from_language=source_lang if source_lang != 'auto' else 'en',
                    to_language=target_lang,
                    timeout=self.timeout
                )
                return result
            except Exception as e2:
                print(f"Fallback translator error: {e2}")
                return None
    
    def is_available(self) -> bool:
        """Check if translation service is available"""
        try:
            # Test with a simple translation
            result = ts.translate_text(
                query_text="test",
                translator=self.translator_name,
                from_language='en',
                to_language='ar',
                timeout=2
            )
            return result is not None
        except:
            return False


# Example usage
if __name__ == "__main__":
    translator = LibreTranslator()
    
    # Test translation
    test_text = "heart"
    result = translator.translate(test_text, source_lang='en', target_lang='ar')
    
    if result:
        print(f"✅ Translation: {test_text} → {result}")
    else:
        print(f"❌ Translation failed")
    
    # Check availability
    if translator.is_available():
        print("✅ LibreTranslate is available")
    else:
        print("❌ LibreTranslate is not available")
