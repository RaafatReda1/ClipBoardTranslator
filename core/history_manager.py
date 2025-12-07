"""
History and Favorites Manager
Handles storage and retrieval of translation history and user favorites
"""

import json
import os
from datetime import datetime
from collections import Counter

class HistoryManager:
    """
    Manages translation history and favorites.
    Data is stored in resources/history.json
    """
    
    def __init__(self, storage_file="resources/history.json"):
        self.storage_file = storage_file
        self.history = []
        self.favorites = []
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
        
        self.load_data()
        
    def load_data(self):
        """Load history and favorites from disk"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = data.get('history', [])
                    self.favorites = data.get('favorites', [])
            except Exception as e:
                print(f"Error loading history: {e}")
                self.history = []
                self.favorites = []
                
    def save_data(self):
        """Save history and favorites to disk"""
        try:
            data = {
                'history': self.history,
                'favorites': self.favorites
            }
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
            
    def add_entry(self, original, translation, source):
        """Add a translation entry to history"""
        entry = {
            'original': original,
            'translation': translation,
            'source': source,
            'timestamp': datetime.now().isoformat(),
            'id': f"{datetime.now().timestamp()}"
        }
        
        # Add to beginning of list
        self.history.insert(0, entry)
        
        # Limit history size (e.g. 1000 entries)
        if len(self.history) > 1000:
            self.history = self.history[:1000]
            
        self.save_data()
        return entry
        
    def add_favorite(self, entry):
        """Add an entry to favorites"""
        # Check if already exists
        for fav in self.favorites:
            if fav['original'] == entry['original']:
                return False
                
        # Add timestamp if missing (backward compatibility)
        if 'added_at' not in entry:
            entry['added_at'] = datetime.now().isoformat()
            
        self.favorites.insert(0, entry)
        self.save_data()
        return True
        
    def remove_favorite(self, original_text):
        """Remove from favorites"""
        initial_len = len(self.favorites)
        self.favorites = [f for f in self.favorites if f['original'] != original_text]
        if len(self.favorites) != initial_len:
            self.save_data()
            return True
        return False
        
    def is_favorite(self, original_text):
        """Check if text is in favorites"""
        return any(f['original'] == original_text for f in self.favorites)
        
    def toogle_favorite(self, entry):
        """Toggle favorite status"""
        if self.is_favorite(entry['original']):
            self.remove_favorite(entry['original'])
            return False
        else:
            self.add_favorite(entry)
            return True
            
    def get_history(self, limit=50):
        """Get recent history"""
        return self.history[:limit]
        
    def get_favorites(self):
        """Get all favorites"""
        return self.favorites
        
    def clear_history(self):
        """Clear all history"""
        self.history = []
        self.save_data()
        
    def get_statistics(self):
        """Get usage statistics"""
        total_translations = len(self.history)
        total_favorites = len(self.favorites)
        
        if not self.history:
            return {
                'total_translations': 0,
                'total_favorites': 0,
                'top_source': 'None',
                'words_translated': 0
            }
            
        # Analyze sources
        sources = [h['source'] for h in self.history]
        source_counts = Counter(sources)
        top_source = source_counts.most_common(1)[0][0] if source_counts else "None"
        
        # Estimate words based on length (very rough approximation)
        total_chars = sum(len(h['original']) for h in self.history)
        
        return {
            'total_translations': total_translations,
            'total_favorites': total_favorites,
            'top_source': top_source,
            'avg_length': round(total_chars / total_translations) if total_translations else 0
        }
