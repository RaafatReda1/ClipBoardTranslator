import sys
import logging
import requests
import socket
import ssl
import json
from utils.config_manager import ConfigManager

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Diagnostic")

def check_dns():
    print("\n--- 1. Checking DNS Resolution ---")
    try:
        ip = socket.gethostbyname("openrouter.ai")
        print(f"DNS Resolved 'openrouter.ai' to {ip}")
        return True
    except Exception as e:
        print(f"DNS Resolution Failed: {e}")
        return False

def check_ssl():
    print("\n--- 2. Checking SSL Connection ---")
    try:
        response = requests.get("https://openrouter.ai", timeout=5)
        print(f"SSL Handshake Successful (Status: {response.status_code})")
        return True
    except requests.exceptions.SSLError as e:
        print(f"SSL Error: {e}")
        print("   -> Suggestion: Enable verify=False workaround")
        return False
    except Exception as e:
        print(f"Connection Error: {e}")
        return False

def check_model_access(api_key, model_name):
    print(f"\n--- Testing Model: {model_name} ---")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://medtranslate-pro.app",
        "X-Title": "MedTranslate Pro"
    }
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "Say 'Health'."}]
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            if content:
                print(f"SUCCESS! Response: {content.strip()}")
                return True
            else:
                print(f"API returned 200 OK but EMPTY content. Raw: {data}")
                return False
        else:
            print(f"FAILED. Status: {response.status_code}")
            print(f"   Body: {response.text}")
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False

def run_diagnostics():
    print("MEDTRANSLATE PRO - DEEP DIAGNOSTICS")
    
    if not check_dns():
        return
    
    if not check_ssl():
        print("SSL failures detected. Network might be restricted.")
        
    # Load Config
    print("\n--- 3. Loading Configuration ---")
    try:
        cm = ConfigManager()
        api_key = cm.config.get('openrouter', {}).get('api_key')
        current_model = cm.config.get('openrouter', {}).get('model')
        
        if not api_key:
            print("No API Key found in config!")
            return
            
        print(f"API Key found: {api_key[:8]}...")
        print(f"Current Configured Model: {current_model}")
        
        # Test Current Model
        print(f"\n--- 4. Testing Configured Model ({current_model}) ---")
        if check_model_access(api_key, current_model):
            print("   -> Current model configuration IS working.")
        else:
            print("   -> Current model FAILING.")
            
            # Test Alternative Models
            print("\n--- 5. Testing Alternatives ---")
            alternatives = [
                "google/gemini-2.0-flash-exp:free",
                "meta-llama/llama-3-8b-instruct:free",
                "mistralai/mistral-7b-instruct:free"
            ]
            
            for alt in alternatives:
                if check_model_access(api_key, alt):
                    print(f"   -> RECOMMENDATION: Switch to {alt}")
                    
                    # Force switch in config if found
                    print("   -> APPLYING FIX: Switching model automatically.")
                    cm.config['openrouter']['model'] = alt
                    cm.save_config()
                    print(f"   -> FIXED: Active model is now {alt}")
                    break
                    
    except Exception as e:
        print(f"Config Error: {e}")

if __name__ == "__main__":
    run_diagnostics()
