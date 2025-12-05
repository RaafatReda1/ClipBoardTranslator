"""
Theme Manager for MedTranslate Pro
Handles application theming and styling
"""

import json
import os
from typing import Dict, Optional


class ThemeManager:
    """Manages application themes"""
    
    def __init__(self, themes_path: str = "resources/themes/default_themes.json"):
        """
        Initialize theme manager
        
        Args:
            themes_path: Path to themes JSON file
        """
        self.themes_path = themes_path
        self.themes = self.load_themes()
        self.current_theme_name = "dark_minimal"
        self.current_theme = self.themes.get(self.current_theme_name, {})
    
    def load_themes(self) -> Dict:
        """Load themes from JSON file"""
        if not os.path.exists(self.themes_path):
            print(f"Warning: Themes file not found: {self.themes_path}")
            return self._get_default_themes()
        
        try:
            with open(self.themes_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading themes: {e}")
            return self._get_default_themes()
    
    def _get_default_themes(self) -> Dict:
        """Get default themes as fallback"""
        return {
            "dark_minimal": {
                "name": "Dark Minimal",
                "bg": "#1e1e1e",
                "surface": "#252525",
                "border": "#007acc",
                "text": "#ffffff",
                "text_secondary": "#cccccc",
                "accent": "#4ec9b0",
                "success": "#50fa7b",
                "error": "#ff5555",
                "warning": "#ffb86c"
            }
        }
    
    def set_theme(self, theme_name: str) -> bool:
        """
        Set current theme
        
        Args:
            theme_name: Name of theme to activate
        
        Returns:
            True if successful, False otherwise
        """
        if theme_name in self.themes:
            self.current_theme_name = theme_name
            self.current_theme = self.themes[theme_name]
            return True
        else:
            print(f"Theme '{theme_name}' not found")
            return False
    
    def get_color(self, color_name: str, default: str = "#000000") -> str:
        """
        Get color from current theme
        
        Args:
            color_name: Name of color (bg, text, border, etc.)
            default: Default color if not found
        
        Returns:
            Color hex code
        """
        return self.current_theme.get(color_name, default)
    
    def get_stylesheet(self) -> str:
        """
        Get Qt stylesheet for current theme
        
        Returns:
            Qt stylesheet string
        """
        theme = self.current_theme
        
        return f"""
        QWidget {{
            background-color: {theme.get('bg', '#1e1e1e')};
            color: {theme.get('text', '#ffffff')};
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
        }}
        
        QLabel {{
            color: {theme.get('text', '#ffffff')};
            background-color: transparent;
        }}
        
        QPushButton {{
            background-color: {theme.get('accent', '#4ec9b0')};
            color: {theme.get('bg', '#1e1e1e')};
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {theme.get('border', '#007acc')};
        }}
        
        QPushButton:pressed {{
            background-color: {theme.get('surface', '#252525')};
        }}
        
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {theme.get('surface', '#252525')};
            color: {theme.get('text', '#ffffff')};
            border: 1px solid {theme.get('border', '#007acc')};
            border-radius: 4px;
            padding: 6px;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid {theme.get('accent', '#4ec9b0')};
        }}
        
        QComboBox {{
            background-color: {theme.get('surface', '#252525')};
            color: {theme.get('text', '#ffffff')};
            border: 1px solid {theme.get('border', '#007acc')};
            border-radius: 4px;
            padding: 6px;
        }}
        
        QComboBox::drop-down {{
            border: none;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {theme.get('text', '#ffffff')};
        }}
        
        QTabWidget::pane {{
            border: 1px solid {theme.get('border', '#007acc')};
            background-color: {theme.get('bg', '#1e1e1e')};
        }}
        
        QTabBar::tab {{
            background-color: {theme.get('surface', '#252525')};
            color: {theme.get('text_secondary', '#cccccc')};
            padding: 8px 16px;
            border: 1px solid {theme.get('border', '#007acc')};
            border-bottom: none;
        }}
        
        QTabBar::tab:selected {{
            background-color: {theme.get('accent', '#4ec9b0')};
            color: {theme.get('bg', '#1e1e1e')};
        }}
        
        QCheckBox {{
            color: {theme.get('text', '#ffffff')};
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {theme.get('border', '#007acc')};
            border-radius: 3px;
            background-color: {theme.get('surface', '#252525')};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {theme.get('accent', '#4ec9b0')};
        }}
        
        QRadioButton {{
            color: {theme.get('text', '#ffffff')};
            spacing: 8px;
        }}
        
        QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {theme.get('border', '#007acc')};
            border-radius: 9px;
            background-color: {theme.get('surface', '#252525')};
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {theme.get('accent', '#4ec9b0')};
        }}
        
        QScrollBar:vertical {{
            background-color: {theme.get('surface', '#252525')};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {theme.get('border', '#007acc')};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {theme.get('accent', '#4ec9b0')};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        """
    
    def get_available_themes(self) -> list:
        """Get list of available theme names"""
        return list(self.themes.keys())
    
    def add_custom_theme(self, name: str, colors: Dict) -> bool:
        """
        Add a custom theme
        
        Args:
            name: Theme name
            colors: Dictionary of color definitions
        
        Returns:
            True if successful
        """
        try:
            self.themes[name] = colors
            # Save to file
            with open(self.themes_path, 'w', encoding='utf-8') as f:
                json.dump(self.themes, f, indent=4)
            return True
        except Exception as e:
            print(f"Error adding custom theme: {e}")
            return False


# Example usage
if __name__ == "__main__":
    theme_manager = ThemeManager()
    
    print("Available themes:")
    for theme in theme_manager.get_available_themes():
        print(f"  - {theme}")
    
    # Set theme
    theme_manager.set_theme("dark_minimal")
    print(f"\nCurrent theme: {theme_manager.current_theme_name}")
    print(f"Background color: {theme_manager.get_color('bg')}")
