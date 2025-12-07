"""
Configuration Manager for MedTranslate Pro
Handles saving and loading user settings
"""

import json
import os
from typing import Dict, Any


class ConfigManager:
    """Manages application configuration"""
    
    DEFAULT_CONFIG = {
        "version": "1.0.0",
        "general": {
            "auto_start": False,
            "show_notifications": True,
            "play_sound": False,
            "translator_active": False
        },
        "translation": {
            "active_source": "auto",
            "source_priority": ["keyboard_fixer", "openrouter_ai", "libre", "local"],
            "default_source_lang": "auto",
            "default_target_lang": "ar",
            "offline_fallback": True,
            "cache_enabled": True,
            "cache_size": 100
        },
        "popup": {
            "auto_close": True,
            "auto_close_delay": 5,
            "position": "top_right",
            "width": 480,
            "height": 220,
            "opacity": 95,
            "enable_animations": True,
            "font_family": "Segoe UI",
            "font_size": 12
        },
        "openrouter": {
            "api_key": "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",
            "model": "meta-llama/llama-3-8b-instruct:free",
            "system_prompt": "You are a concise medical terminology assistant. When given a medical term:\n1. Provide Arabic translation\n2. Brief 1-2 sentence explanation in Arabic\n3. ONE simple example\n4. Keep under 60 words\n\nFormat your response clearly and concisely.",
            "custom_prompt": "",
            "max_tokens": 150,
            "temperature": 0.7,
            "include_examples": True
        },
        "hotkeys": {
            "start_translator": "ctrl+shift+1",
            "stop_translator": "ctrl+shift+2",
            "cycle_sources": "ctrl+shift+3",
            "force_ai": "ctrl+shift+a",
            "force_libre": "ctrl+shift+l",
            "force_local": "ctrl+shift+d",
            "force_keyfix": "ctrl+shift+k",
            "copy_result": "ctrl+alt+c",
            "pin_window": "ctrl+alt+p",
            "open_settings": "ctrl+alt+s",
            "toggle_tab": "ctrl+alt+t"
        },
        "appearance": {
            "theme": "dark_minimal",
            "custom_colors": None
        },
        "advanced": {
            "network_timeout": 5,
            "retry_attempts": 3,
            "enable_logging": True,
            "log_level": "INFO",
            "check_updates": True
        },
        "dictionaries": {
            "medical_terms_path": "dictionary.json",
            "preload_at_startup": True
        }
    }
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize config manager"""
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return self._merge_configs(self.DEFAULT_CONFIG, loaded_config)
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Recursively merge loaded config with defaults"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self, config: Dict[str, Any] = None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, *keys, default=None):
        """Get nested configuration value"""
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, *keys, value):
        """Set nested configuration value"""
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self.save_config()
    
    def update_section(self, section: str, data: Dict):
        """Update entire configuration section"""
        if section in self.config:
            self.config[section].update(data)
            self.save_config()
