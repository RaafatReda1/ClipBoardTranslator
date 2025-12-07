"""
Splash Screen for MedTranslate Pro
Beautiful loading screen with animations
"""

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QProgressBar, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor, QPainter, QLinearGradient


class SplashScreen(QWidget):
    """Premium splash screen with loading animation"""
    
    def __init__(self, theme_manager):
        """Initialize splash screen"""
        super().__init__()
        self.theme_manager = theme_manager
        self.progress = 0
        
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        """Setup splash screen UI"""
        # Window properties
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(450, 300)
        
        # Center on screen
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Logo/Icon
        logo_label = QLabel("🏥")
        logo_label.setFont(QFont("Segoe UI", 60))
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Title
        title_label = QLabel("MedTranslate Pro")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {self.theme_manager.get_color('accent')};")
        
        # Subtitle
        subtitle_label = QLabel("Medical Translation Assistant")
        subtitle_label.setFont(QFont("Segoe UI", 12))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet(f"color: {self.theme_manager.get_color('text_secondary')};")
        
        # Loading message
        self.loading_label = QLabel("Initializing...")
        self.loading_label.setFont(QFont("Segoe UI", 10))
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet(f"color: {self.theme_manager.get_color('text')};")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {self.theme_manager.get_color('surface')};
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.theme_manager.get_color('accent')},
                    stop:1 {self.theme_manager.get_color('success')}
                );
                border-radius: 4px;
            }}
        """)
        
        # Version label
        version_label = QLabel("v1.0.0")
        version_label.setFont(QFont("Segoe UI", 8))
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet(f"color: {self.theme_manager.get_color('text_secondary')};")
        
        # Add to layout
        layout.addStretch()
        layout.addWidget(logo_label)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addStretch()
        layout.addWidget(self.loading_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(version_label)
        
        self.setLayout(layout)
        
        # Add drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)
    
    def setup_animations(self):
        """Setup fade in animation"""
        from PySide6.QtWidgets import QGraphicsOpacityEffect
        
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(500)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.OutCubic)
    
    def paintEvent(self, event):
        """Custom paint for rounded background"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(self.theme_manager.get_color('bg')))
        gradient.setColorAt(1, QColor(self.theme_manager.get_color('surface')))
        
        # Draw rounded rectangle
        painter.setBrush(gradient)
        painter.setPen(QColor(self.theme_manager.get_color('border')))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 20, 20)
    
    def show_with_animation(self):
        """Show splash with fade in"""
        self.show()
        self.fade_in.start()
    
    def update_progress(self, value, message=""):
        """Update progress bar and message"""
        self.progress = value
        self.progress_bar.setValue(value)
        if message:
            self.loading_label.setText(message)
    
    def finish(self):
        """Close splash screen with fade out"""
        from PySide6.QtWidgets import QGraphicsOpacityEffect
        
        fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        fade_out.setDuration(400)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.InCubic)
        fade_out.finished.connect(self.close)
        fade_out.start()
