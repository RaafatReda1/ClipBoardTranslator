"""
Clipboard Monitor for MedTranslate Pro
Monitors clipboard changes and triggers translations
"""

import pyperclip
import time
from typing import Callable, Optional
from PySide6.QtCore import QThread, Signal


class ClipboardMonitor(QThread):
    """Monitors clipboard for changes"""
    
    # Signal emitted when new text is copied
    text_copied = Signal(str)
    
    def __init__(self, check_interval: float = 0.1):
        """
        Initialize clipboard monitor
        
        Args:
            check_interval: How often to check clipboard (seconds)
        """
        super().__init__()
        self.check_interval = check_interval
        self.last_text = ""
        self.is_active = False
        self.is_running = True
    
    def run(self):
        """Main monitoring loop"""
        while self.is_running:
            if self.is_active:
                try:
                    current_text = pyperclip.paste()
                    
                    # Check if text changed and is not empty
                    if current_text and current_text != self.last_text:
                        self.last_text = current_text
                        self.text_copied.emit(current_text)
                
                except Exception as e:
                    print(f"Clipboard monitor error: {e}")
            
            time.sleep(self.check_interval)
    
    def start_monitoring(self):
        """Start monitoring clipboard"""
        self.is_active = True
        self.last_text = ""  # Reset to catch current clipboard
    
    def stop_monitoring(self):
        """Stop monitoring clipboard"""
        self.is_active = False
    
    def stop(self):
        """Stop the thread"""
        self.is_running = False
        self.wait()
    
    def is_monitoring(self) -> bool:
        """Check if currently monitoring"""
        return self.is_active
