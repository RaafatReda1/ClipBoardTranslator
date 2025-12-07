import sys
import logging
from utils.config_manager import ConfigManager
from core.openrouter_ai import OpenRouterAI

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("AI_Debug")

def test_ai_integration():
    print("--- Starting AI Integration Test ---")
    
    # 1. Load Config
    config_manager = ConfigManager()
    config = config_manager.config
    
    ai_config = config.get('openrouter', {})
    api_key = ai_config.get('api_key')
    model = ai_config.get('model')
    
    print(f"API Key present: {bool(api_key)}")
    print(f"Target Model: {model}")
    
    if not api_key or "YOUR_API_KEY" in api_key:
        print("ERROR: Invalid API Key")
        return

    # 2. Initialize AI Core
    # FIXED: Pass arguments correctly
    ai = OpenRouterAI(
        api_key=api_key, 
        model=model
    )
    
    # 3. Test Translation
    test_text = "myocardial infarction"
    print(f"\nAttempting to translate: '{test_text}'")
    
    try:
        result = ai.translate(test_text)
        if result:
            print(f"SUCCESS! Result: {result}")
        else:
            print("FAILURE: Returned None or empty string")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    test_ai_integration()
