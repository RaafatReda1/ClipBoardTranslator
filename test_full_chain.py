import sys
import logging
from utils.config_manager import ConfigManager
from utils.logger import Logger
from core.translation_engine import TranslationEngine

# Setup console logging
logging.basicConfig(level=logging.DEBUG)
# Ensure our custom logger also prints to stdout/file
logger = Logger(log_level='DEBUG')

def test_full_chain():
    print("\n--- FULL CHAIN AI TEST ---")
    
    # 1. Load Config
    config_manager = ConfigManager()
    config = config_manager.config
    
    # 2. Force AI configuration
    config['translation']['active_source'] = 'openrouter_ai'
    
    print(f"Active Source set to: {config['translation']['active_source']}")
    
    # 3. Initialize Engine
    print("Initializing TranslationEngine...")
    engine = TranslationEngine(config, logger)
    
    # 4. Attempt Translation
    test_word = "myocardial infarction"
    print(f"\nTranslating: '{test_word}'")
    
    result, source = engine.translate(test_word)
    
    print("\n--- RESULT ---")
    print(f"Source used: {source}")
    print(f"Translation length: {len(result)}")
    print(f"Content: {result[:100]}...")
    
    if source == 'openrouter_ai' and len(result) > 10:
        print("\nIT IS WORKING!")
    else:
        print("\nIT IS NOT WORKING properly.")
        if source != 'openrouter_ai':
            print(f"Reason: It fell back to '{source}' instead of using AI.")
            # Check if AI was considered available
            if hasattr(engine, 'openrouter_ai'):
                avail = engine.openrouter_ai.is_available()
                print(f"DEBUG: engine.openrouter_ai.is_available() returned: {avail}")
            else:
                print("DEBUG: engine.openrouter_ai does not exist")

if __name__ == "__main__":
    test_full_chain()
