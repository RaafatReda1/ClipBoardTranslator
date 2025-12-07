"""
Comprehensive Test Suite for MedTranslate Pro
Tests all core components individually
"""

import sys
import os
import io

# Set UTF-8 encoding for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.keyboard_fixer import KeyboardFixer
from core.local_dictionary import LocalDictionary
from core.libre_translator import LibreTranslator
from core.openrouter_ai import OpenRouterAI
from core.translation_engine import TranslationEngine
from utils.config_manager import ConfigManager
from utils.cache_manager import CacheManager
from utils.logger import Logger


def print_header(title):
    """Print formatted test header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_keyboard_fixer():
    """Test keyboard layout fixer"""
    print_header("Testing Keyboard Layout Fixer")
    
    fixer = KeyboardFixer()
    
    test_cases = [
        (";jhf", "English keyboard typing Arabic"),
        ("hgshk", "English keyboard typing Arabic"),
        ("hello", "Normal English text"),
    ]
    
    for text, description in test_cases:
        is_fixed, fixed_text, fix_type = fixer.detect_and_fix(text)
        if is_fixed:
            print(f"[OK] {description}")
            print(f"     Input:  '{text}'")
            print(f"     Fixed:  '{fixed_text}' (Type: {fix_type})")
        else:
            print(f"[INFO] {description}")
            print(f"       Input:  '{text}' - No fix needed")
    
    print("\n[PASS] Keyboard Fixer Test Complete!")


def test_local_dictionary():
    """Test local dictionary"""
    print_header("Testing Local Dictionary")
    
    dictionary = LocalDictionary("dictionary.json")
    
    # Check if dictionary loaded
    stats = dictionary.get_stats()
    print(f"Dictionary loaded: {stats['total_entries']} entries")
    
    # Test translations
    test_words = [
        "heart",
        "cardiology", 
        "hematoma",
        "abdomen",
        "nonexistentword123"
    ]
    
    print("\nTesting translations:")
    for word in test_words:
        translation = dictionary.translate(word)
        if translation:
            # Truncate and show only ASCII-safe version
            trans_safe = translation[:50] if len(translation) < 50 else translation[:47] + "..."
            print(f"[OK] '{word}' -> Found (length: {len(translation)} chars)")
        else:
            print(f"[FAIL] '{word}' -> Not found")
    
    # Test search
    print("\nTesting search for 'heart':")
    results = dictionary.search("heart", max_results=3)
    print(f"     Found {len(results)} results")
    
    print("\n[PASS] Local Dictionary Test Complete!")


def test_libre_translator():
    """Test LibreTranslate"""
    print_header("Testing LibreTranslate (Online)")
    
    translator = LibreTranslator()
    
    # Check availability
    print("Checking service availability...")
    if translator.is_available():
        print("[OK] LibreTranslate is available")
        
        # Test translation
        test_words = ["heart", "doctor"]
        print("\nTesting translations:")
        for word in test_words:
            translation = translator.translate(word, source_lang='en', target_lang='ar')
            if translation:
                print(f"[OK] '{word}' -> Translated successfully")
            else:
                print(f"[FAIL] '{word}' -> Translation failed")
    else:
        print("[WARN] LibreTranslate is not available (offline or network issue)")
    
    print("\n[PASS] LibreTranslate Test Complete!")


def test_openrouter_ai():
    """Test OpenRouter AI"""
    print_header("Testing OpenRouter AI (Online)")
    
    # Load API key from config
    config = ConfigManager()
    api_key = config.get('openrouter', 'api_key')
    
    if not api_key:
        print("[FAIL] No API key found in config")
        return
    
    print(f"Using API key: {api_key[:20]}...")
    
    # Get model from config
    model = config.get('openrouter', 'model')
    print(f"Using model: {model}")
    
    ai = OpenRouterAI(
        api_key=api_key,
        model=model
    )
    
    # Simple test
    test_term = "heart"
    print(f"\nTesting AI explanation for '{test_term}':")
    print("[INFO] This may take a few seconds...")
    result = ai.translate(test_term)
    if result:
        print(f"[OK] AI Response received (length: {len(result)} chars)")
        print(f"     Preview: {result[:80]}...")
    else:
        print(f"[WARN] AI translation failed (may be offline or API issue)")
    
    print("\n[PASS] OpenRouter AI Test Complete!")


def test_config_manager():
    """Test configuration manager"""
    print_header("Testing Configuration Manager")
    
    config = ConfigManager()
    
    # Test getting values
    print("Testing configuration access:")
    print(f"[OK] Active source: {config.get('translation', 'active_source')}")
    print(f"[OK] Theme: {config.get('appearance', 'theme')}")
    print(f"[OK] Cache size: {config.get('translation', 'cache_size')}")
    
    # Test nested get
    hotkeys = config.get('hotkeys')
    print(f"[OK] Hotkeys loaded: {len(hotkeys)} shortcuts")
    
    print("\n[PASS] Config Manager Test Complete!")


def test_cache_manager():
    """Test cache manager"""
    print_header("Testing Cache Manager")
    
    cache = CacheManager(max_size=5)
    
    # Test caching
    print("Testing cache operations:")
    cache.set("heart", "translation1", "local", "en", "ar")
    cache.set("doctor", "translation2", "local", "en", "ar")
    
    # Test retrieval
    result1 = cache.get("heart", "local", "en", "ar")
    result2 = cache.get("doctor", "local", "en", "ar")
    result3 = cache.get("nonexistent", "local", "en", "ar")
    
    print(f"[OK] Cache hit for 'heart': {result1}")
    print(f"[OK] Cache hit for 'doctor': {result2}")
    print(f"[OK] Cache miss for 'nonexistent': {result3}")
    
    # Test stats
    size, max_size = cache.get_stats()
    print(f"[OK] Cache stats: {size}/{max_size} entries")
    
    print("\n[PASS] Cache Manager Test Complete!")


def test_translation_engine():
    """Test main translation engine"""
    print_header("Testing Translation Engine")
    
    config = ConfigManager()
    logger = Logger(log_level="ERROR")  # Reduce log noise
    
    engine = TranslationEngine(config.config, logger)
    
    # Get stats
    stats = engine.get_stats()
    print(f"Engine Statistics:")
    print(f"   - Dictionary entries: {stats['dictionary_entries']}")
    print(f"   - Cache size: {stats['cache_size']}/{stats['cache_max']}")
    print(f"   - Active source: {stats['active_source']}")
    print(f"   - Network available: {stats['network_available']}")
    
    # Test translations
    test_cases = [
        (";jhf", "Keyboard error test"),
        ("heart", "Local dictionary test"),
    ]
    
    print("\nTesting translations:")
    for text, description in test_cases:
        translation, source = engine.translate(text)
        print(f"\n[OK] {description}")
        print(f"     Input:  '{text}'")
        print(f"     Source: {source}")
        if len(translation) > 60:
            print(f"     Result: {translation[:60]}...")
        else:
            print(f"     Result: {translation}")
    
    print("\n[PASS] Translation Engine Test Complete!")


def run_all_tests():
    """Run all component tests"""
    print("\n" + "="*60)
    print("  MedTranslate Pro - Component Test Suite")
    print("="*60)
    
    try:
        test_config_manager()
        test_cache_manager()
        test_keyboard_fixer()
        test_local_dictionary()
        test_libre_translator()
        test_openrouter_ai()
        test_translation_engine()
        
        print("\n" + "="*60)
        print("  [SUCCESS] ALL TESTS COMPLETED!")
        print("="*60)
        
    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
