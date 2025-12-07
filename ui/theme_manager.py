"""
Theme Manager for MedTranslate Pro
Handles application theming and styling with a comprehensive visual system
"""

import json
import os
from typing import Dict, Any, Optional


class ThemeManager:
    """Manages application themes with comprehensive color system"""
    
    def __init__(self, themes_path: str = "resources/themes/themes.json"):
        """
        Initialize theme manager
        
        Args:
            themes_path: Path to themes JSON file
        """
        self.themes_path = themes_path
        self.default_themes = self._get_default_themes()
        self.themes = self.default_themes.copy()
        
        # Load custom/saved themes
        loaded = self.load_themes()
        if loaded:
            # Merge loaded with defaults (don't overwrite structure if loaded is legacy)
            # Actually, standard is to update. 
            self.themes.update(loaded)
            
        self.current_theme_name = "dark_minimal"
        self.current_theme = self.themes.get(self.current_theme_name, self.themes["dark_minimal"])
    
    def load_themes(self) -> Dict:
        """Load themes from JSON file"""
        if not os.path.exists(self.themes_path):
            return {}
        
        try:
            with open(self.themes_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
            
    def _get_default_themes(self) -> Dict:
        """Get 5 Professional Themes"""
        return {
            "dark_minimal": {
                "name": "Dark Minimal",
                "background": {
                    "primary": "#0f0f0f",
                    "secondary": "#1a1a1a",
                    "tertiary": "#262626",
                    "elevated": "#2a2a2a"
                },
                "text": {
                    "primary": "#ffffff", 
                    "secondary": "#a1a1aa",
                    "tertiary": "#52525b",
                    "disabled": "#3f3f46",
                    "inverse": "#000000"
                },
                "semantic": {
                    "success": "#10b981",
                    "warning": "#f59e0b",
                    "error": "#ef4444",
                    "info": "#3b82f6",
                    "accent": "#8b5cf6" # Purple
                },
                "border": "#27272a",
                "sources": {
                    "libre": "#3b82f6",
                    "openrouter_ai": "#8b5cf6",
                    "local": "#10b981",
                    "keyboard_fixer": "#f59e0b",
                    "auto": "#6366f1"
                }
            },
            
            "light_professional": {
                "name": "Light Professional",
                "background": {
                    "primary": "#ffffff",
                    "secondary": "#f8f9fa",
                    "tertiary": "#e9ecef",
                    "elevated": "#ffffff"
                },
                "text": {
                    "primary": "#1f2937",
                    "secondary": "#6b7280",
                    "tertiary": "#9ca3af",
                    "disabled": "#d1d5db",
                    "inverse": "#ffffff"
                },
                "semantic": {
                    "success": "#059669",
                    "warning": "#d97706",
                    "error": "#dc2626",
                    "info": "#2563eb",
                    "accent": "#3b82f6" # Blue
                },
                "border": "#e5e7eb",
                "sources": {"libre": "#3b82f6", "openrouter_ai": "#8b5cf6", "local": "#10b981", "keyboard_fixer": "#f59e0b", "auto": "#6366f1"}
            },
            
            "deep_ocean": {
                "name": "Deep Ocean",
                "background": {
                    "primary": "#0a1929",
                    "secondary": "#132f4c",
                    "tertiary": "#173a5e",
                    "elevated": "#1e4976"
                },
                "text": {
                    "primary": "#e2e8f0",
                    "secondary": "#94a3b8",
                    "tertiary": "#64748b",
                    "disabled": "#475569",
                    "inverse": "#0f172a"
                },
                "semantic": {
                    "success": "#4ade80",
                    "warning": "#fbbf24",
                    "error": "#f87171",
                    "info": "#60a5fa",
                    "accent": "#06b6d4" # Cyan
                },
                "border": "#1e4976",
                "sources": {"libre": "#3b82f6", "openrouter_ai": "#8b5cf6", "local": "#10b981", "keyboard_fixer": "#f59e0b", "auto": "#6366f1"}
            },
            
            "warm_sunset": {
                "name": "Warm Sunset",
                "background": {
                    "primary": "#1a0f1f",
                    "secondary": "#2d1b3d",
                    "tertiary": "#432454",
                    "elevated": "#3b2149"
                },
                "text": {
                    "primary": "#fdf4ff",
                    "secondary": "#e8d5f0",
                    "tertiary": "#cba6d6",
                    "disabled": "#83658f",
                    "inverse": "#1a0f1f"
                },
                "semantic": {
                    "success": "#34d399",
                    "warning": "#fbbf24",
                    "error": "#fb7185",
                    "info": "#818cf8",
                    "accent": "#ff6b35" # Orange
                },
                "border": "#56326e",
                "sources": {"libre": "#3b82f6", "openrouter_ai": "#8b5cf6", "local": "#10b981", "keyboard_fixer": "#f59e0b", "auto": "#6366f1"}
            },
            
            "medical_blue": {
                "name": "Medical Blue",
                "background": {
                    "primary": "#f0f8ff",
                    "secondary": "#e6f2ff",
                    "tertiary": "#cfe4fc",
                    "elevated": "#ffffff"
                },
                "text": {
                    "primary": "#0c4a6e",
                    "secondary": "#0369a1",
                    "tertiary": "#38bdf8",
                    "disabled": "#bae6fd",
                    "inverse": "#ffffff"
                },
                "semantic": {
                    "success": "#0ea5e9",
                    "warning": "#f59e0b",
                    "error": "#ef4444",
                    "info": "#0284c7",
                    "accent": "#1e90ff" # Medical Blue
                },
                "border": "#bfdbfe",
                "sources": {"libre": "#3b82f6", "openrouter_ai": "#8b5cf6", "local": "#10b981", "keyboard_fixer": "#f59e0b", "auto": "#6366f1"}
            }
        }
    
    def set_theme(self, theme_name: str) -> bool:
        """Set current theme"""
        if theme_name in self.themes:
            self.current_theme_name = theme_name
            self.current_theme = self.themes[theme_name]
            return True
        return False
    
    def get_color(self, color_name: str, default: str = "#000000") -> str:
        """
        Get color supporting nested dot notation and legacy mapping.
        Example: 'text.primary' or 'semantic.success'
        """
        # 1. Try Legacy Mapping
        legacy_map = {
            'bg': 'background.primary',
            'surface': 'background.secondary',
            'text': 'text.primary',
            'text_secondary': 'text.secondary',
            'accent': 'semantic.accent',
            'success': 'semantic.success',
            'error': 'semantic.error',
            'warning': 'semantic.warning',
            'border': 'border'
        }
        
        path = legacy_map.get(color_name, color_name)
        
        # 2. Traverse nested dict
        try:
            val = self.current_theme
            for key in path.split('.'):
                val = val.get(key, {})
            
            if isinstance(val, str):
                return val
        except:
            pass
            
        return default
        
    def get_available_themes(self) -> list:
        return list(self.themes.keys())

    def get_stylesheet(self) -> str:
        """Get Qt stylesheet for current theme"""
        bg = self.get_color('background.primary')
        bg_sec = self.get_color('background.secondary')
        text = self.get_color('text.primary')
        text_sec = self.get_color('text.secondary')
        accent = self.get_color('semantic.accent')
        border = self.get_color('border')
        
        return f"""
        QWidget {{
            background-color: {bg};
            color: {text};
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
        }}
        
        QLabel {{
            color: {text};
            background-color: transparent;
        }}
        
        QPushButton {{
            background-color: {accent};
            color: {self.get_color('text.inverse')};
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 600;
        }}
        
        QPushButton:hover {{
            opacity: 0.9;
        }}
        
        QLineEdit, QTextEdit, QPlainTextEdit, QListWidget {{
            background-color: {bg_sec};
            color: {text};
            border: 1px solid {border};
            border-radius: 6px;
            padding: 8px;
        }}
        
        QLineEdit:focus, QTextEdit:focus {{
            border: 2px solid {accent};
        }}
        
        QComboBox {{
            background-color: {bg_sec};
            color: {text};
            border: 1px solid {border};
            border-radius: 6px;
            padding: 6px 12px;
        }}
        
        QCheckBox {{
            color: {text};
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {border};
            border-radius: 4px;
            background-color: {bg_sec};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {accent};
            border-color: {accent};
        }}
        
        QScrollBar:vertical {{
            background-color: {bg};
            width: 12px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {border};
            border-radius: 6px;
            min-height: 20px;
            margin: 2px;
        }}
        
        QTabWidget::pane {{
            border: 1px solid {border};
            background-color: {bg};
        }}
        
        QTabBar::tab {{
            background-color: {bg_sec};
            color: {text_sec};
            padding: 10px 20px;
            border: 1px solid {border};
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {bg};
            color: {accent};
            border-bottom: 2px solid {accent};
        }}
        """

if __name__ == "__main__":
    tm = ThemeManager()
    print("Themes:", tm.get_available_themes())
    tm.set_theme("deep_ocean")
    print("Current Accent:", tm.get_color("semantic.accent"))
    print("Legacy Accent:", tm.get_color("accent"))
