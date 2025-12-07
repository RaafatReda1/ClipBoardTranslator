"""
Clean Translation Popup for MedTranslate Pro
Simple, beautiful, and functional
Includes Favorites support & Scrolling for long text
"""

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QFrame, QSizePolicy
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QFont
import pyperclip


class TranslationPopup(QWidget):
    """Clean and simple translation popup"""
    
    def __init__(self, config, theme_manager, history_manager):
        """Initialize popup"""
        super().__init__()
        self.config = config
        self.theme_manager = theme_manager
        self.history_manager = history_manager
        self.is_pinned = False
        self.current_translation = ""
        self.current_original = ""
        self.current_source = ""
        
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        """Setup clean UI"""
        # Window properties
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        
        # Size - Increased for better readability
        self.setFixedSize(400, 250)
        
        # Clean stylesheet
        bg = self.theme_manager.get_color('bg')
        text = self.theme_manager.get_color('text')
        accent = self.theme_manager.get_color('accent')
        success = self.theme_manager.get_color('success')
        
        self.setStyleSheet(f"""
            QWidget#MainPopup {{
                background-color: {bg};
                border: 2px solid {accent};
                border-radius: 12px;
            }}
            QLabel {{
                background: transparent;
                color: {text};
            }}
            QPushButton {{
                background-color: {accent};
                color: {bg};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {success};
            }}
            QPushButton#CloseBtn {{
                background-color: transparent;
                color: {self.theme_manager.get_color('error')};
                font-size: 20px;
                padding: 0;
            }}
            QPushButton#CloseBtn:hover {{
                background-color: {self.theme_manager.get_color('error')};
                color: white;
                border-radius: 4px;
            }}
            QPushButton#FavBtn {{
                background-color: transparent;
                color: {self.theme_manager.get_color('text_secondary')};
                font-size: 18px;
                padding: 0;
                width: 30px;
            }}
            QPushButton#FavBtn:hover {{
                border: 1px solid {self.theme_manager.get_color('border')};
                border-radius: 15px;
            }}
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {bg};
                width: 8px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.theme_manager.get_color('border')};
                min-height: 20px;
                border-radius: 4px;
            }}
        """)
        
        self.setObjectName("MainPopup")
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Scroll Area for Content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(5, 0, 5, 0)
        
        # Translation text (main focus)
        self.translation_text = QLabel()
        self.translation_text.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.translation_text.setWordWrap(True)
        self.translation_text.setAlignment(Qt.AlignCenter)
        self.translation_text.setStyleSheet(f"color: {success};")
        self.translation_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        # Original text (smaller)
        self.original_text = QLabel()
        self.original_text.setFont(QFont("Segoe UI", 10))
        self.original_text.setWordWrap(True)
        self.original_text.setAlignment(Qt.AlignCenter)
        self.original_text.setStyleSheet(f"color: {self.theme_manager.get_color('text_secondary')}; margin-top: 10px;")
        
        content_layout.addWidget(self.translation_text)
        content_layout.addWidget(self.original_text)
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        # Divider line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet(f"background-color: {self.theme_manager.get_color('border')};")
        layout.addWidget(line)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.clicked.connect(self.copy_translation)
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        
        self.pin_btn = QPushButton("Pin")
        self.pin_btn.clicked.connect(self.toggle_pin)
        self.pin_btn.setCursor(Qt.PointingHandCursor)
        self.pin_btn.setFixedWidth(60)
        
        # Favorite Button
        self.fav_btn = QPushButton("❤")
        self.fav_btn.setObjectName("FavBtn")
        self.fav_btn.setFixedSize(30, 30)
        self.fav_btn.clicked.connect(self.toggle_favorite)
        self.fav_btn.setCursor(Qt.PointingHandCursor)
        self.fav_btn.setToolTip("Add to Favorites")
        
        self.close_btn = QPushButton("×")
        self.close_btn.setObjectName("CloseBtn")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.clicked.connect(self.close_popup)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        
        btn_layout.addWidget(self.copy_btn)
        btn_layout.addWidget(self.pin_btn)
        btn_layout.addWidget(self.fav_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.close_btn)
        
        layout.addLayout(btn_layout)
        
        self.position_window()
    
    def setup_animations(self):
        """Setup simple fade animation"""
        self.setWindowOpacity(0)
        
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(200)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(0.95)
        self.fade_in.setEasingCurve(QEasingCurve.OutCubic)
        
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(150)
        self.fade_out.setStartValue(0.95)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.InCubic)
        self.fade_out.finished.connect(self.hide)
        
        self.auto_close_timer = QTimer(self)
        self.auto_close_timer.timeout.connect(self.close_popup)
    
    def position_window(self):
        """Position at top-right"""
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        
        # Get position from config
        pos_setting = self.config.get('popup', {}).get('position', 'top_right')
        margin = 30
        
        if pos_setting == 'top_right':
            x = screen.width() - self.width() - margin
            y = margin
        elif pos_setting == 'top_left':
            x = margin
            y = margin
        elif pos_setting == 'bottom_right':
            x = screen.width() - self.width() - margin
            y = screen.height() - self.height() - margin
        elif pos_setting == 'bottom_left':
            x = margin
            y = screen.height() - self.height() - margin
        else: # center
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2
            
        self.move(x, y)
    
    def keyPressEvent(self, event):
        """Handle keys"""
        # Esc always closes
        if event.key() == Qt.Key_Escape:
            self.close_popup()
        # Ctrl key press closes if enabled
        elif event.key() == Qt.Key_Control:
             if self.config.get('popup', {}).get('close_on_ctrl_click', True):
                self.close_popup()
            
    def mousePressEvent(self, event):
        """Handle mouse click"""
        # Ctrl + Click to close (Robust backup for "Clicking Ctrl")
        if event.modifiers() & Qt.ControlModifier:
            if self.config.get('popup', {}).get('close_on_ctrl_click', True):
                self.close_popup()
                return
        super().mousePressEvent(event)
        
    def focusOutEvent(self, event):
        """Handle losing focus (click outside)"""
        # If enabled in settings, close on click outside even if pinned
        close_on_outside = self.config.get('popup', {}).get('close_on_outside_click', False)
        if close_on_outside:
             self.close_popup()
        super().focusOutEvent(event)
        
    def show_translation(self, original, translation, source):
        """Show translation"""
        # ... existing code ...
        self.translation_text.setText(translation) # No truncation
        self.original_text.setText(f"Original: {original}\nSource: {source}")
        
        self.current_translation = translation
        self.current_original = original
        self.current_source = source
        
        # Update favorite button state
        self.update_fav_button()
        
        # RTL support
        if self.is_arabic(translation):
            self.translation_text.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.translation_text.setLayoutDirection(Qt.RightToLeft)
        else:
            self.translation_text.setAlignment(Qt.AlignCenter)
            self.translation_text.setLayoutDirection(Qt.LeftToRight)
        
        # Show with fade
        self.show()
        self.raise_()
        self.activateWindow() # Ensure it gets focus to detect outside clicks
        self.fade_in.start()
        
        # Auto-close (restart timer if re-shown)
        if hasattr(self, 'auto_close_timer') and self.auto_close_timer.isActive():
            self.auto_close_timer.stop()
            
        if not self.is_pinned and self.config.get('popup', {}).get('auto_close', True):
            delay = self.config.get('popup', {}).get('auto_close_delay', 5) * 1000
            self.auto_close_timer.start(delay)
    
    def is_arabic(self, text):
        """Check for Arabic"""
        return any('\u0600' <= c <= '\u06FF' for c in text)
    
    def copy_translation(self):
        """Copy to clipboard"""
        if self.current_translation:
            pyperclip.copy(self.current_translation)
            self.copy_btn.setText("✓ Copied")
            QTimer.singleShot(1000, lambda: self.copy_btn.setText("Copy"))
    
    def toggle_pin(self):
        """Toggle pin"""
        self.is_pinned = not self.is_pinned
        if self.is_pinned:
            self.pin_btn.setText("Unpin")
            self.auto_close_timer.stop()
            self.setStyleSheet(self.styleSheet().replace(f"border: 2px solid {self.theme_manager.get_color('accent')}", f"border: 2px solid {self.theme_manager.get_color('success')}"))
        else:
            self.pin_btn.setText("Pin")
            self.setStyleSheet(self.styleSheet().replace(f"border: 2px solid {self.theme_manager.get_color('success')}", f"border: 2px solid {self.theme_manager.get_color('accent')}"))
            
    def toggle_favorite(self):
        """Toggle favorite status"""
        if not self.current_original:
            return
            
        entry = {
            'original': self.current_original,
            'translation': self.current_translation,
            'source': self.current_source
        }
        
        self.history_manager.toogle_favorite(entry)
        self.update_fav_button()
        
    def update_fav_button(self):
        """Update favorite button appearance"""
        if self.history_manager.is_favorite(self.current_original):
            self.fav_btn.setStyleSheet(f"""
                QPushButton#FavBtn {{
                    background-color: transparent;
                    color: {self.theme_manager.get_color('error')};
                    font-size: 18px;
                    padding: 0;
                }}
            """)
        else:
            self.fav_btn.setStyleSheet(f"""
                QPushButton#FavBtn {{
                    background-color: transparent;
                    color: {self.theme_manager.get_color('text_secondary')};
                    font-size: 18px;
                    padding: 0;
                }}
                QPushButton#FavBtn:hover {{
                    border: 1px solid {self.theme_manager.get_color('border')};
                    border-radius: 15px;
                }}
            """)
    
    def close_popup(self):
        """Close with fade"""
        self.auto_close_timer.stop()
        self.fade_out.start()
    
