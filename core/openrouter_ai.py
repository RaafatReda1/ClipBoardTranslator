"""
OpenRouter AI Integration for MedTranslate Pro
Provides detailed medical term explanations using AI
"""

import requests
from typing import Optional


class OpenRouterAI:
    """Handles OpenRouter AI API calls"""
    
    def __init__(self, api_key: str, model: str = "meta-llama/llama-3-8b-instruct:free",
                 system_prompt: str = "", custom_prompt: str = "", 
                 max_tokens: int = 150, temperature: float = 0.7):
        """
        Initialize OpenRouter AI
        
        Args:
            api_key: OpenRouter API key
            model: Model to use (free models available)
            system_prompt: Default system prompt
            custom_prompt: User's custom prompt override
            max_tokens: Maximum response length
            temperature: Creativity level (0-1)
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Default system prompt
        self.default_system_prompt = """You are a concise medical terminology assistant. When given a medical term:
1. Provide Arabic translation
2. Brief 1-2 sentence explanation in Arabic
3. ONE simple example
4. Keep under 60 words

Format your response clearly and concisely."""
        
        self.system_prompt = system_prompt or self.default_system_prompt
        self.custom_prompt = custom_prompt
    
    def translate(self, text: str) -> Optional[str]:
        """
        Get AI explanation for medical term
        
        Args:
            text: Medical term to explain
        
        Returns:
            AI-generated explanation or None if error
        """
        import logging
        logger = logging.getLogger("MedTranslatePro.AI")
        
        try:
            # Combine system prompt with custom prompt
            full_system_prompt = self.system_prompt
            if self.custom_prompt:
                full_system_prompt += f"\n\nAdditional instructions: {self.custom_prompt}"
            
            # Prepare request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://medtranslate-pro.app",
                "X-Title": "MedTranslate Pro"
            }
            
            # Merge system prompt into user message for better compatibility with some models
            combined_prompt = f"{full_system_prompt}\n\nTerm to explain: {text}"
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": combined_prompt}
                ]
            }
            
            import time
            
            max_retries = 2
            retry_delay = 1
            
            for attempt in range(max_retries + 1):
                try:
                    logger.debug(f"Sending AI request for: {text} (Attempt {attempt+1}/{max_retries+1})")
                    
                    # Make request
                    response = requests.post(
                        self.base_url,
                        headers=headers,
                        json=payload,
                        timeout=20
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Robust extraction
                        choices = data.get('choices', [])
                        if not choices:
                            logger.warning(f"AI Response attempt {attempt+1} contained no choices. RAW: {data}")
                            if attempt < max_retries:
                                time.sleep(retry_delay)
                                continue
                            return None
                            
                        message = choices[0].get('message', {})
                        content = message.get('content', '')
                        
                        if not content:
                            logger.warning(f"AI Response attempt {attempt+1} contained empty content.")
                            if attempt < max_retries:
                                time.sleep(retry_delay)
                                continue
                            return None
                            
                        return content
                        
                    elif response.status_code == 429: # Rate limit
                        logger.warning("AI Rate Limited (429). Retrying...")
                        if attempt < max_retries:
                            time.sleep(retry_delay * 2) # Wait longer for rate limits
                            continue
                    else:
                        logger.error(f"API Error {response.status_code}: {response.text[:200]}")
                        
                except requests.exceptions.Timeout:
                    logger.warning("OpenRouter AI request timed out.")
                except Exception as e:
                    logger.error(f"OpenRouter AI attempt {attempt+1} failed: {e}")
                
                # Check if we should retry
                if attempt < max_retries:
                    time.sleep(retry_delay)
                    retry_delay *= 2 # Exponential backoff
            
            return None
        
        except requests.exceptions.Timeout:
            logger.error("OpenRouter AI request timed out")
            return None
        except Exception as e:
            logger.error(f"OpenRouter AI exceptional error: {e}", exc_info=True)
            return None
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 5
            }
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def update_prompts(self, system_prompt: str = None, custom_prompt: str = None):
        """Update system and custom prompts"""
        if system_prompt is not None:
            self.system_prompt = system_prompt
        if custom_prompt is not None:
            self.custom_prompt = custom_prompt


# Example usage
if __name__ == "__main__":
    # Use the provided API key
    api_key = "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"
    ai = OpenRouterAI(api_key=api_key)
    
    # Test translation
    test_term = "cardiology"
    result = ai.translate(test_term)
    
    if result:
        print(f"✅ AI Explanation for '{test_term}':")
        print(result)
    else:
        print(f"❌ AI translation failed")
    
    # Check availability
    if ai.is_available():
        print("\n✅ OpenRouter AI is available")
    else:
        print("\n❌ OpenRouter AI is not available")
