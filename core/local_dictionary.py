"""
Local Dictionary for MedTranslate Pro
Handles offline dictionary lookups with fuzzy matching
"""

import json
import os
import re
from typing import Optional, Dict
from difflib import get_close_matches


class LocalDictionary:
    """Manages local offline dictionary"""
    
    def __init__(self, dictionary_path: str = "dictionary.json"):
        """Initialize local dictionary"""
        self.dictionary_path = dictionary_path
        self.dictionary: Dict[str, str] = {}
        self.load_dictionary()
    
    def load_dictionary(self):
        """Load dictionary from JSON file"""
        if not os.path.exists(self.dictionary_path):
            print(f"Warning: Dictionary file not found: {self.dictionary_path}")
            return
        
        try:
            with open(self.dictionary_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                # Preprocess keys for faster lookup
                self.dictionary = {
                    self._preprocess_text(key): value 
                    for key, value in data.items()
                }
            print(f"✅ Loaded {len(self.dictionary)} dictionary entries")
        except Exception as e:
            print(f"Error loading dictionary: {e}")
            self.dictionary = {}
    
    def _preprocess_text(self, text: str) -> str:
        """Normalize text for lookup"""
        # Remove punctuation and convert to lowercase
        return re.sub(r'[^\w\s]', '', text.lower()).strip()
    
    def translate(self, text: str) -> Optional[str]:
        """
        Translate text using local dictionary
        
        Returns:
            Translation if found, None otherwise
        """
        processed_text = self._preprocess_text(text)
        
        # Try exact match first
        if processed_text in self.dictionary:
            return self.dictionary[processed_text]
        
        # Try fuzzy matching
        closest_matches = get_close_matches(
            processed_text, 
            self.dictionary.keys(), 
            n=1, 
            cutoff=0.6
        )
        
        if closest_matches:
            match = closest_matches[0]
            translation = self.dictionary[match]
            # Return with the matched term for clarity
            return f"{match}: {translation}"
        
        return None
    
    def search(self, query: str, max_results: int = 5) -> list:
        """
        Search dictionary for terms containing query
        
        Returns:
            List of (term, translation) tuples
        """
        processed_query = self._preprocess_text(query)
        results = []
        
        for term, translation in self.dictionary.items():
            if processed_query in term:
                results.append((term, translation))
                if len(results) >= max_results:
                    break
        
        return results
    
    def get_stats(self) -> Dict[str, int]:
        """Get dictionary statistics"""
        return {
            "total_entries": len(self.dictionary),
            "loaded": len(self.dictionary) > 0
        }


# Example usage
if __name__ == "__main__":
    dictionary = LocalDictionary("dictionary.json")
    
    # Test translations
    test_words = ["heart", "cardiology", "hematoma", "abdomen"]
    
    for word in test_words:
        translation = dictionary.translate(word)
        if translation:
            print(f"✅ {word} → {translation}")
        else:
            print(f"❌ {word} → Not found")
