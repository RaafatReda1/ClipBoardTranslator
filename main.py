"""
MedTranslate Pro - Main Application
Entry point for the medical translation assistant
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread, QTimer

# Import core components
from core.clipboard_monitor import ClipboardMonitor
from core.translation_engine import TranslationEngine
from core.hotkey_manager import HotkeyManager
from core.history_manager import HistoryManager

# Import UI components
from ui.system_tray import SystemTray
from ui.popup_window import TranslationPopup
from ui.floating_tab import FloatingTab
from ui.theme_manager import ThemeManager

# Import utilities
from utils.config_manager import ConfigManager
from utils.logger import Logger
import pyperclip


class MedTranslateApp:
    """Main application class"""
    
    def __init__(self):
        """Initialize application"""
        # Create Qt Application
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setApplicationName("MedTranslate Pro")
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        
        # Load configuration
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config
        
        # Initialize logger
        log_level = self.config.get('advanced', {}).get('log_level', 'INFO')
        self.logger = Logger(log_level=log_level)
        self.logger.info("Starting MedTranslate Pro...")
        
        # Apply theme
        theme_name = self.config.get('appearance', {}).get('theme', 'dark_minimal')
        self.theme_manager.set_theme(theme_name)
        
        # Initialize translation engine
        self.translation_engine = TranslationEngine(self.config, self.logger)
        
        # Initialize History Manager
        self.history_manager = HistoryManager()
        
        # Initialize UI components
        self.setup_ui()
        
        # Initialize clipboard monitor
        self.setup_clipboard_monitor()
        
        # Initialize hotkey manager
        self.setup_hotkeys()
        
        self.logger.info("MedTranslate Pro initialized successfully")
    
    def setup_ui(self):
        """Setup UI components"""
        # System tray
        self.system_tray = SystemTray(self.app, self.config)
        self.system_tray.activate_translator.connect(self.activate_translator)
        self.system_tray.deactivate_translator.connect(self.deactivate_translator)
        self.system_tray.change_source.connect(self.change_translation_source)
        self.system_tray.open_settings.connect(self.open_settings)
        self.system_tray.quit_application.connect(self.quit_application)
        
        # Translation popup
        self.popup = TranslationPopup(self.config, self.theme_manager, self.history_manager)
        
        # Floating tab
        self.floating_tab = FloatingTab(self.config, self.theme_manager)
        self.floating_tab.settings_clicked.connect(self.open_settings)
        self.floating_tab.toggle_translator.connect(self.toggle_translator_from_tab)
        self.floating_tab.show()
        
        self.logger.info("UI components initialized")
    
    def setup_clipboard_monitor(self):
        """Setup clipboard monitoring"""
        self.clipboard_monitor = ClipboardMonitor()
        self.clipboard_monitor.text_copied.connect(self.on_text_copied)
        self.clipboard_monitor.start()
        
        self.logger.info("Clipboard monitor started")
    
    def setup_hotkeys(self):
        """Setup global hotkeys"""
        self.hotkey_manager = HotkeyManager(self.config)
        
        # Register hotkeys
        self.hotkey_manager.register_hotkey('start_translator', self.activate_translator)
        self.hotkey_manager.register_hotkey('stop_translator', self.deactivate_translator)
        self.hotkey_manager.register_hotkey('open_settings', self.open_settings)
        
        # Source switching hotkeys
        self.hotkey_manager.register_hotkey('force_ai', 
                                           lambda: self.change_translation_source('openrouter_ai'))
        self.hotkey_manager.register_hotkey('force_libre', 
                                           lambda: self.change_translation_source('libre'))
        self.hotkey_manager.register_hotkey('force_local', 
                                           lambda: self.change_translation_source('local'))
        self.hotkey_manager.register_hotkey('force_keyfix', 
                                           lambda: self.change_translation_source('keyboard_fixer'))
        
        # Result actions
        self.hotkey_manager.register_hotkey('copy_result', self.copy_current_result)
        
        self.logger.info("Hotkeys registered")
    
    def activate_translator(self):
        """Activate translator"""
        self.clipboard_monitor.start_monitoring()
        self.system_tray.update_status(True)
        self.floating_tab.update_status(True)
        self.system_tray.show_notification(
            "MedTranslate Pro",
            "Translator activated! Copy any text to translate.",
            3000
        )
        self.logger.info("Translator activated")
    
    def deactivate_translator(self):
        """Deactivate translator"""
        self.clipboard_monitor.stop_monitoring()
        self.system_tray.update_status(False)
        self.floating_tab.update_status(False)
        self.system_tray.show_notification(
            "MedTranslate Pro",
            "Translator deactivated.",
            2000
        )
        self.logger.info("Translator deactivated")
    
    def toggle_translator_from_tab(self):
        """Toggle translator from floating tab"""
        if self.clipboard_monitor.is_monitoring():
            self.deactivate_translator()
        else:
            self.activate_translator()
    
    def change_translation_source(self, source):
        """Change active translation source"""
        self.config['translation']['active_source'] = source
        self.translation_engine.update_config(self.config)
        self.config_manager.save_config()
        
        source_names = {
            'auto': 'Auto (Smart)',
            'keyboard_fixer': 'Keyboard Fixer',
            'openrouter_ai': 'OpenRouter AI',
            'libre': 'LibreTranslate',
            'local': 'Local Dictionary'
        }
        
        self.system_tray.show_notification(
            "Translation Source Changed",
            f"Now using: {source_names.get(source, source)}",
            2000
        )
        self.logger.info(f"Translation source changed to: {source}")
    
    def on_text_copied(self, text):
        """Handle text copied event"""
        if not self.clipboard_monitor.is_monitoring():
            return
        
        self.logger.debug(f"Text copied: {text[:50]}...")
        
        # Translate text
        translation, source = self.translation_engine.translate(text)
        
        # Check for invalid input/error
        if source == "none" or "Invalid input" in translation:
            self.logger.debug(f"Invalid input ignored: {text[:30]}...")
            self.floating_tab.glow_error()
            return
            
        # Auto-copy if fixed
        if source == "keyboard_fixer":
            self.safe_copy(translation)
            self.system_tray.show_notification("Fixed & Copied", translation, 1500)
        
        # Add to history
        self.history_manager.add_entry(text, translation, source)
        
        # Show popup
        self.popup.show_translation(text, translation, source)
        
        # Check for fallback
        preferred = self.config.get('translation', {}).get('active_source', 'auto')
        if preferred != 'auto' and source != preferred and preferred != 'keyboard_fixer':
            self.system_tray.show_notification(
                "Source Fallback",
                f"Preferred source '{preferred}' failed. Used '{source}' instead.",
                3000
            )
        # Show standard notification if enabled
        elif self.config.get('general', {}).get('show_notifications', True):
            self.system_tray.show_notification(
                "Translation Ready",
                f"Translated using {source}",
                1500
            )
    
    def open_settings(self):
        """Open settings window"""
        from ui.settings_window import SettingsWindow
        
        if not hasattr(self, 'settings_window') or not self.settings_window.isVisible():
            self.settings_window = SettingsWindow(
                self.config_manager, 
                self.theme_manager,
                self.history_manager
            )
            self.settings_window.settings_changed.connect(self.on_settings_changed)
            self.settings_window.show()
        else:
            self.settings_window.activateWindow()
            
    def on_settings_changed(self, new_config):
        """Handle settings updates"""
        self.config = new_config
        self.translation_engine.update_config(new_config)
        
        # Propagate config to UI components
        if hasattr(self, 'floating_tab'):
            self.floating_tab.update_config(new_config)
        if hasattr(self, 'popup'):
            self.popup.config = new_config
            
        self.logger.info("Settings updated via Settings Window")
        
        # Re-register hotkeys if changed
        self.setup_hotkeys()
        
        # Apply theme if changed
        theme_name = new_config.get('appearance', {}).get('theme', 'dark_minimal')
        self.theme_manager.set_theme(theme_name)
        
        # Show notification
        self.system_tray.show_notification("Settings", "Configuration updated successfully", 2000)
    
    def copy_current_result(self):
        """Copy current translation result to clipboard"""
        if hasattr(self, 'popup') and self.popup.current_translation:
             self.safe_copy(self.popup.current_translation)
             self.system_tray.show_notification("Copied", "Translation copied to clipboard", 1000)

    def safe_copy(self, text):
        """Copy to clipboard without triggering monitor"""
        if not text: return
        
        was_monitoring = self.clipboard_monitor.is_monitoring()
        if was_monitoring:
            self.clipboard_monitor.stop_monitoring()
            
        try:
            pyperclip.copy(text)
            self.clipboard_monitor.last_text = text
        finally:
            if was_monitoring:
                self.clipboard_monitor.start_monitoring()

    def quit_application(self):
        """Quit application"""
        self.logger.info("Shutting down MedTranslate Pro...")
        
        # Stop clipboard monitor
        self.clipboard_monitor.stop()
        
        # Unregister hotkeys
        self.hotkey_manager.unregister_all()
        
        # Save config
        self.config_manager.save_config()
        
        # Quit
        self.app.quit()
    
    def run(self):
        """Run the application"""
        self.logger.info("MedTranslate Pro is running")
        return self.app.exec()


def main():
    """Main entry point"""
    app = MedTranslateApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
