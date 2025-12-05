"""
Keyboard Layout Fixer for MedTranslate Pro
Automatically detects and fixes text typed in wrong keyboard layout
"""

from typing import Tuple, Optional


class KeyboardFixer:
    """Detects and fixes keyboard layout errors"""
    
    def __init__(self):
        """Initialize keyboard mappings"""
        # Arabic → English keyboard mapping
        self.ar_to_en = {
            'ض': 'q', 'ص': 'w', 'ث': 'e', 'ق': 'r', 'ف': 't',
            'غ': 'y', 'ع': 'u', 'ه': 'i', 'خ': 'o', 'ح': 'p',
            'ج': '[', 'د': ']', 'ش': 'a', 'س': 's', 'ي': 'd',
            'ب': 'f', 'ل': 'g', 'ا': 'h', 'ت': 'j', 'ن': 'k',
            'م': 'l', 'ك': ';', 'ط': "'", 'ذ': '`', 'ئ': 'z',
            'ء': 'x', 'ؤ': 'c', 'ر': 'v', 'ى': 'b', 'ة': 'n',
            'و': 'm', 'ز': ',', 'ظ': '.', '÷': '/',
            'َ': 'Q', 'ً': 'W', 'ُ': 'E', 'ٌ': 'R', 'لإ': 'T',
            'إ': 'Y', ''': 'U', 'آ': 'O', '×': 'P', '؛': '<',
            'ـ': '_', 'ِ': 'A', 'ٍ': 'S', ']': 'D', '[': 'F',
            'لأ': 'G', 'أ': 'H', 'ـ': 'J', '،': 'K', '/': 'L',
            ':': ':', '"': '"', '~': '~', 'ْ': 'Z', '}': 'X',
            '{': 'C', 'لآ': 'V', 'لا': 'B', 'لى': 'N', 'لا': 'M',
            '،': '<', '.': '>', '؟': '?'
        }
        
        # English → Arabic (reverse mapping)
        self.en_to_ar = {v: k for k, v in self.ar_to_en.items()}
        
        # Additional common mappings
        self.en_to_ar.update({
            'q': 'ض', 'w': 'ص', 'e': 'ث', 'r': 'ق', 't': 'ف',
            'y': 'غ', 'u': 'ع', 'i': 'ه', 'o': 'خ', 'p': 'ح',
            '[': 'ج', ']': 'د', 'a': 'ش', 's': 'س', 'd': 'ي',
            'f': 'ب', 'g': 'ل', 'h': 'ا', 'j': 'ت', 'k': 'ن',
            'l': 'م', ';': 'ك', "'": 'ط', '`': 'ذ', 'z': 'ئ',
            'x': 'ء', 'c': 'ؤ', 'v': 'ر', 'b': 'ى', 'n': 'ة',
            'm': 'و', ',': 'ز', '.': 'ظ', '/': '÷'
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
        
        # Check for English keyboard typing Arabic
        en_to_ar_score = self._calculate_en_to_ar_score(text)
        
        # Check for Arabic keyboard typing English
        ar_to_en_score = self._calculate_ar_to_en_score(text)
        
        # Determine which fix to apply
        if en_to_ar_score > 0.3:  # 30% suspicious chars
            fixed = self._convert(text, self.en_to_ar)
            return True, fixed, 'en_to_ar'
        
        elif ar_to_en_score > 0.5:  # 50% Arabic chars
            fixed = self._convert(text, self.ar_to_en)
            # Check if result looks more like English
            if self._looks_like_english(fixed):
                return True, fixed, 'ar_to_en'
        
        return False, text, 'none'
    
    def _calculate_en_to_ar_score(self, text: str) -> float:
        """Calculate probability that English keyboard was used for Arabic"""
        suspicious_chars = [';', "'", '[', ']', '`', ',', '.', '/']
        score = sum(1 for c in text if c in suspicious_chars)
        return score / len(text) if len(text) > 0 else 0
    
    def _calculate_ar_to_en_score(self, text: str) -> float:
        """Calculate probability that Arabic keyboard was used for English"""
        arabic_chars = "ضصثقفغعهخحجدشسيبلاتنمكطئءؤرلاىةوزظ"
        arabic_count = sum(1 for c in text if c in arabic_chars)
        return arabic_count / len(text) if len(text) > 0 else 0
    
    def _looks_like_english(self, text: str) -> bool:
        """Check if text looks like English words"""
        # Simple heuristic: check if mostly ASCII letters
        ascii_count = sum(1 for c in text if c.isascii() and c.isalpha())
        return ascii_count / len(text) > 0.7 if len(text) > 0 else False
    
    def _convert(self, text: str, mapping: dict) -> str:
        """Apply character mapping"""
        result = []
        for char in text:
            result.append(mapping.get(char, char))
        return ''.join(result)
    
    def is_keyboard_error(self, text: str) -> bool:
        """Quick check if text might be a keyboard error"""
        is_fixed, _, _ = self.detect_and_fix(text)
        return is_fixed


# Example usage and testing
if __name__ == "__main__":
    fixer = KeyboardFixer()
    
    # Test cases
    test_cases = [
        ";jhf",  # Should convert to كتاب
        "hgshk",  # Should convert to السلام
        "ضصثق",  # Should convert to qwer
    ]
    
    for test in test_cases:
        is_fixed, fixed_text, fix_type = fixer.detect_and_fix(test)
        if is_fixed:
            print(f"✅ Fixed: '{test}' → '{fixed_text}' (Type: {fix_type})")
        else:
            print(f"❌ No fix needed: '{test}'")
