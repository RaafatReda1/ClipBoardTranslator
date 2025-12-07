import sys
import logging
import json
from utils.config_manager import ConfigManager
import requests

# Setup logging
logging.basicConfig(level=logging.DEBUG)

def test_ai_integration():
    print("--- AI DEEP DEBUG ---")
    
    # 1. Load Config
    config_manager = ConfigManager()
    config = config_manager.config
    
    ai_config = config.get('openrouter', {})
    api_key = ai_config.get('api_key')
    model = ai_config.get('model')
    
    if not api_key:
        print("ERROR: No API Key found")
        return

    print(f"API Key: {api_key[:10]}...")
    print(f"Model: {model}")

    # 2. RAW REQUEST (Bypassing class to see raw output)
    print("\n--- Sending Raw Request ---")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://medtranslate-pro.app",
        "X-Title": "MedTranslate Pro"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Explain 'Myocardial Infarction' in 1 sentence."}
        ]
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15,
            verify=False 
        )
        
        print(f"Status Code: {response.status_code}")
        print("Raw Response Body:")
        
        try:
            # Pretty print JSON
            data = response.json()
            print(json.dumps(data, indent=2))
            
            # Check structure matches expectation
            if 'choices' in data:
                print("\nCHECK: 'choices' field found")
                if len(data['choices']) > 0:
                    print("CHECK: 'choices' list is not empty")
                    if 'message' in data['choices'][0]:
                        print("CHECK: 'message' field found")
                        content = data['choices'][0]['message'].get('content', '')
                        if content:
                             print(f"CONTENT PREVIEW: {content[:50]}...")
                        else:
                             print("CHECK: Content is EMPTY/NULL")
                    else:
                        print("FAIL: 'message' field MISSING in choice")
                else:
                    print("FAIL: 'choices' list is EMPTY")
            elif 'error' in data:
                 print(f"FAIL: API returned ERROR: {data['error']}")
            else:
                print("FAIL: 'choices' field MISSING")
                
        except json.JSONDecodeError:
            print("FAIL: Response is NOT valid JSON")
            print(response.text)
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    test_ai_integration()
