"""
Keyboard Layout Fixer for MedTranslate Pro
Automatically detects and fixes text typed in wrong keyboard layout
"""

from typing import Tuple, Optional


class KeyboardFixer:
    """Detects and fixes keyboard layout errors"""
    
    def __init__(self):
        """Initialize keyboard mappings"""
        # Arabic → English keyboard mapping (Standard 101)
        self.ar_to_en = {
            'ض': 'q', 'ص': 'w', 'ث': 'e', 'ق': 'r', 'ف': 't',
            'غ': 'y', 'ع': 'u', 'ه': 'i', 'خ': 'o', 'ح': 'p',
            'ج': '[', 'د': ']', 'ش': 'a', 'س': 's', 'ي': 'd',
            'ب': 'f', 'ل': 'g', 'ا': 'h', 'ت': 'j', 'ن': 'k',
            'م': 'l', 'ك': ';', 'ط': "'", 'ذ': '`', 
            'ئ': 'z', 'ء': 'x', 'ؤ': 'c', 'ر': 'v', 
            'لا': 'b', 'لآ': 'b', 'لأ': 'G', # B maps to لا usually (Lam+Alif)
            'ى': 'n', 'ة': 'm', 'و': ',', 'ز': '.', 'ظ': '/',
            '؟': '?', '،': '<', '؛': 'P', '×': 'O', '÷': 'I'
        }
        
        # English → Arabic (reverse mapping)
        self.en_to_ar = {v: k for k, v in self.ar_to_en.items()}
        
        # Explicit corrections for common QWERTY/AR101 variations
        self.en_to_ar.update({
            'q': 'ض', 'w': 'ص', 'e': 'ث', 'r': 'ق', 't': 'ف',
            'y': 'غ', 'u': 'ع', 'i': 'ه', 'o': 'خ', 'p': 'ح',
            '[': 'ج', ']': 'د', 'a': 'ش', 's': 'س', 'd': 'ي',
            'f': 'ب', 'g': 'ل', 'h': 'ا', 'j': 'ت', 'k': 'ن',
            'l': 'م', ';': 'ك', "'": 'ط', '`': 'ذ', 'z': 'ئ',
            'x': 'ء', 'c': 'ؤ', 'v': 'ر', 
            'b': 'لا', 'n': 'ى', 'm': 'ة', ',': 'و', '.': 'ز', '/': 'ظ',
            '?': '؟'
        })

    def detect_and_fix(self, text: str) -> Tuple[bool, str, str]:
        """
        Detect if keyboard layout is wrong and fix it
        
        Returns:
            (is_fixed, corrected_text, detected_type)
            detected_type: 'en_to_ar', 'ar_to_en', or 'none'
        """
        if not text or len(text) == 0:
            return False, text, 'none'
            
        # 1. Try treating as Gibberish EN -> AR
        # (Input looks like English chars but meant to be Arabic)
        if self._looks_like_english_gibberish(text):
            fixed_ar = self._convert(text, self.en_to_ar)
            # If the output looks like valid Arabic, accept it
            if self._looks_like_arabic(fixed_ar):
                 return True, fixed_ar, 'en_to_ar'
                 
        # 2. Try treating as Gibberish AR -> EN
        # (Input looks like Arabic chars but meant to be English)
        if self._looks_like_arabic(text):
            fixed_en = self._convert(text, self.ar_to_en)
            # If the output looks like valid English
            if self._looks_like_english(fixed_en):
                 return True, fixed_en, 'ar_to_en'
                 
        # 3. Aggressive Fallback for short texts (like "Desktop" -> "يثسنفخح")
        # If input is clearly one lang but converts to valid other lang
        # check scores
        
        return False, text, 'none'

    def _looks_like_english_gibberish(self, text: str) -> bool:
        """Check if text is mostly English punctuation/letters but meaningless?"""
        # Heuristic: mostly ascii
        ascii_count = sum(1 for c in text if c.isascii())
        return ascii_count / len(text) > 0.8
        
    def _looks_like_arabic(self, text: str) -> bool:
        """Check if text contains Arabic letters"""
        arabic_chars = "ضصثقفغعهخحجدشسيبلاتنمكطئءؤرلاىةوزظ"
        count = sum(1 for c in text if c in arabic_chars or c in 'ًٌٍَُِّْ')
        return count / len(text) > 0.3 # Low threshold to catch even partial matches

    def _looks_like_english(self, text: str) -> bool:
        """Check if text looks like English words"""
        # Simple heuristic: check if mostly ASCII letters
        ascii_count = sum(1 for c in text if c.isascii() and c.isalpha())
        return ascii_count / len(text) > 0.6 if len(text) > 0 else False
    
    def _convert(self, text: str, mapping: dict) -> str:
        """Apply character mapping"""
        result = []
        i = 0
        while i < len(text):
            char = text[i]
            if char in mapping:
                result.append(mapping[char])
            else:
                result.append(char)
            i += 1
        return ''.join(result)
    
    def is_keyboard_error(self, text: str) -> bool:
        """Quick check if text might be a keyboard error"""
        is_fixed, _, _ = self.detect_and_fix(text)
        return is_fixed


if __name__ == "__main__":
    fixer = KeyboardFixer()
    
    # Test cases
    test_cases = [
        ";jhf",  # Should convert to كتاب
        "hgshk",  # Should convert to السلام
        "لاخخن", # Should convert to book (maps b to لا)
        "يثسنفخح", # Should convert to desktop
    ]
    
    for test in test_cases:
        is_fixed, fixed_text, fix_type = fixer.detect_and_fix(test)
        if is_fixed:
            print(f"✅ Fixed: '{test}' → '{fixed_text}' (Type: {fix_type})")
        else:
            print(f"❌ No fix needed: '{test}'")
