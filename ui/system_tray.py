"""
System Tray for MedTranslate Pro
Manages the system tray icon and menu
"""

from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QObject, Signal
import os


class SystemTray(QObject):
    """System tray icon and menu manager"""
    
    # Signals
    activate_translator = Signal()
    deactivate_translator = Signal()
    open_settings = Signal()
    quit_application = Signal()
    change_source = Signal(str)
    
    def __init__(self, app, config):
        """
        Initialize system tray
        
        Args:
            app: QApplication instance
            config: Configuration dictionary
        """
        super().__init__()
        self.app = app
        self.config = config
        self.is_active = False
        
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self.app)
        self.setup_icon()
        self.setup_menu()
        
        # Show tray icon
        self.tray_icon.show()
    
    def setup_icon(self):
        """Setup tray icon"""
        # Try to load custom icon, fallback to default
        icon_path = "resources/icons/app_icon.png"
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
        else:
            # Use default icon (you can create a simple colored circle)
            icon = self.create_default_icon()
        
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("MedTranslate Pro - Inactive")
    
    def create_default_icon(self):
        """Create a default icon if custom icon not found"""
        from PySide6.QtGui import QPixmap, QPainter, QColor
        from PySide6.QtCore import Qt
        
        # Create a simple colored circle as icon
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw circle (gray for inactive)
        color = QColor("#808080")  # Gray
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(4, 4, 56, 56)
        
        painter.end()
        return QIcon(pixmap)
    
    def setup_menu(self):
        """Setup context menu"""
        menu = QMenu()
        
        # Translator status section
        self.status_action = QAction("⚫ Translator: Inactive", menu)
        self.status_action.setEnabled(False)
        menu.addAction(self.status_action)
        
        menu.addSeparator()
        
        # Control actions
        self.activate_action = QAction("▶️ Activate Translator", menu)
        self.activate_action.triggered.connect(self._on_activate)
        menu.addAction(self.activate_action)
        
        self.deactivate_action = QAction("⏸️ Deactivate Translator", menu)
        self.deactivate_action.triggered.connect(self._on_deactivate)
        self.deactivate_action.setEnabled(False)
        menu.addAction(self.deactivate_action)
        
        menu.addSeparator()
        
        # Translation source submenu
        source_menu = menu.addMenu("🔄 Translation Source")
        
        sources = [
            ("Auto (Smart)", "auto"),
            ("Keyboard Fixer", "keyboard_fixer"),
            ("OpenRouter AI", "openrouter_ai"),
            ("LibreTranslate", "libre"),
            ("Local Dictionary", "local")
        ]
        
        self.source_actions = {}
        for name, source_id in sources:
            action = QAction(name, source_menu)
            action.setCheckable(True)
            action.triggered.connect(lambda checked, s=source_id: self._on_source_change(s))
            source_menu.addAction(action)
            self.source_actions[source_id] = action
        
        # Set current source as checked
        current_source = self.config.get('translation', {}).get('active_source', 'auto')
        if current_source in self.source_actions:
            self.source_actions[current_source].setChecked(True)
        
        menu.addSeparator()
        
        # Settings
        settings_action = QAction("⚙️ Settings", menu)
        settings_action.triggered.connect(self._on_settings)
        menu.addAction(settings_action)
        
        # About
        about_action = QAction("ℹ️ About", menu)
        about_action.triggered.connect(self._on_about)
        menu.addAction(about_action)
        
        menu.addSeparator()
        
        # Quit
        quit_action = QAction("❌ Exit", menu)
        quit_action.triggered.connect(self._on_quit)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
    
    def _on_activate(self):
        """Handle activate translator"""
        self.is_active = True
        self.update_status(True)
        self.activate_translator.emit()
    
    def _on_deactivate(self):
        """Handle deactivate translator"""
        self.is_active = False
        self.update_status(False)
        self.deactivate_translator.emit()
    
    def _on_source_change(self, source_id):
        """Handle translation source change"""
        # Uncheck all other sources
        for sid, action in self.source_actions.items():
            action.setChecked(sid == source_id)
        
        self.change_source.emit(source_id)
    
    def _on_settings(self):
        """Handle settings menu"""
        self.open_settings.emit()
    
    def _on_about(self):
        """Handle about menu"""
        from PySide6.QtWidgets import QMessageBox
        
        msg = QMessageBox()
        msg.setWindowTitle("About MedTranslate Pro")
        msg.setText("<h2>MedTranslate Pro</h2>")
        msg.setInformativeText(
            "<p><b>Version:</b> 1.0.0</p>"
            "<p><b>Author:</b> Raafat Reda</p>"
            "<p><b>Email:</b> rafat2782005@gmail.com</p>"
            "<p><b>Phone:</b> 01022779263</p>"
            "<br>"
            "<p>A powerful medical translation assistant with 4 intelligent sources:</p>"
            "<ul>"
            "<li>Keyboard Layout Fixer</li>"
            "<li>Local Dictionary (87,000+ terms)</li>"
            "<li>LibreTranslate (Online)</li>"
            "<li>OpenRouter AI</li>"
            "</ul>"
        )
        msg.setIcon(QMessageBox.Information)
        msg.exec()
    
    def _on_quit(self):
        """Handle quit application"""
        self.quit_application.emit()
    
    def update_status(self, is_active):
        """Update tray icon and menu based on translator status"""
        self.is_active = is_active
        
        if is_active:
            self.status_action.setText("🟢 Translator: Active")
            self.tray_icon.setToolTip("MedTranslate Pro - Active")
            self.activate_action.setEnabled(False)
            self.deactivate_action.setEnabled(True)
            
            # Update icon to green
            self.tray_icon.setIcon(self.create_status_icon("#50fa7b"))  # Green
        else:
            self.status_action.setText("⚫ Translator: Inactive")
            self.tray_icon.setToolTip("MedTranslate Pro - Inactive")
            self.activate_action.setEnabled(True)
            self.deactivate_action.setEnabled(False)
            
            # Update icon to gray
            self.tray_icon.setIcon(self.create_status_icon("#808080"))  # Gray
    
    def create_status_icon(self, color_hex):
        """Create status icon with specific color"""
        from PySide6.QtGui import QPixmap, QPainter, QColor
        from PySide6.QtCore import Qt
        
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw circle
        color = QColor(color_hex)
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(4, 4, 56, 56)
        
        painter.end()
        return QIcon(pixmap)
    
    def show_notification(self, title, message, duration=3000):
        """Show system tray notification"""
        self.tray_icon.showMessage(
            title,
            message,
            QSystemTrayIcon.Information,
            duration
        )
