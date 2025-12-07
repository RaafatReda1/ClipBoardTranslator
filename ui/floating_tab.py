"""
Modern Floating Tab for MedTranslate Pro
Implements Phase 2 Redesign: Idle/Hover states, Semantic Colors, and Touch-friendly
"""

from PySide6.QtWidgets import QWidget, QMenu, QApplication, QToolTip
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QRect, QPoint, QSize, QTimer, QVariantAnimation
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QBrush, QPen, QPainterPath, QFont, QCursor

class FloatingTab(QWidget):
    """
    Modern Floating Tab with specific User interaction zones.
    Idle State: Slim vertical pill.
    Expanded State: Control panel with Source, Toggle, and Settings.
    """
    
    # Signals
    settings_clicked = Signal()
    toggle_translator = Signal()
    
    def __init__(self, config, theme_manager):
        super().__init__()
        self.config = config
        self.theme_manager = theme_manager
        
        # State
        self.is_expanded = False
        self.is_dragging = False
        self.is_active = False # Translator status
        self.drag_start_pos = QPoint()
        self.current_source = "Auto"
        self.error_intensity = 0.0
        
        # Dimensions
        self.WIDTH_IDLE = 12
        self.WIDTH_EXPANDED = 130
        self.HEIGHT_IDLE = 100
        self.HEIGHT_EXPANDED = 140
        self.ANIMATION_DURATION = 200 # ms
        
        self.setup_ui()
        self.update_constraints() # alignment
        
        # Animations
        self.expand_anim = QPropertyAnimation(self, b"geometry")
        self.expand_anim.setDuration(self.ANIMATION_DURATION)
        self.expand_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # Tooltip for status
        self.setMouseTracking(True)
        
    def setup_ui(self):
        """Configure window flags and attributes"""
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.update_status(False) # Init status

    def update_config(self, new_config):
        """Update configuration dynamically"""
        self.config = new_config
        self.update_constraints()
        self.update()

    def update_constraints(self):
        """Read dimensions and positioning from config"""
        ft = self.config.get('floating_tab', {})
        self.HEIGHT_IDLE = ft.get('height', 100)
        self.WIDTH_EXPANDED = ft.get('width_expanded', 130)
        y_pos = ft.get('position_y', 150)
        
        # Snap to left edge for now (Phase 2 default)
        self.setGeometry(0, y_pos, self.WIDTH_IDLE, self.HEIGHT_IDLE)
        
    def update_status(self, is_active: bool):
        """Update visual status (colors)"""
        self.is_active = is_active
        self.update()
        
    def set_source_label(self, label: str):
        """Update source text"""
        self.current_source = label
        self.update()

    # ==========================================
    # Event Handling
    # ==========================================
    
    def enterEvent(self, event):
        """Expand on hover"""
        if not self.is_expanded:
            self.animate_resize(True)
            
    def leaveEvent(self, event):
        """Collapse on leave"""
        if self.is_expanded and not self.is_dragging:
            self.animate_resize(False)
            
    def animate_resize(self, expand: bool):
        """Animate between Idle and Expanded states"""
        self.is_expanded = expand
        
        current_geo = self.geometry()
        target_w = self.WIDTH_EXPANDED if expand else self.WIDTH_IDLE
        target_h = self.HEIGHT_EXPANDED if expand else self.HEIGHT_IDLE
        
        # Keep vertical center overlap or top alignment? 
        # Using top-left constant for simplicity in logic, or adjust Y to center.
        # Let's keep Y constant for now to avoid "jumping" under cursor.
        
        target_rect = QRect(
            current_geo.x(),
            current_geo.y(),
            target_w,
            target_h
        )
        
        self.expand_anim.setStartValue(current_geo)
        self.expand_anim.setEndValue(target_rect)
        self.expand_anim.start()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_start_pos = event.globalPos() - self.frameGeometry().topLeft()
            
            # Click detection for controls (simple zones)
            if self.is_expanded:
                y = event.pos().y()
                h = self.height()
                
                # Zone 1: Settings (Top 1/3)
                if y < h / 3:
                    self.settings_clicked.emit()
                    
                # Zone 2: Toggle (Middle 1/3)
                elif y < 2 * h / 3:
                    self.toggle_translator.emit()
                    
                # Zone 3: Source (Bottom 1/3) - Cycle?
                # For now just info, maybe right click to change?
                
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.globalPos())

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self.move(event.globalPos() - self.drag_start_pos)

    def mouseReleaseEvent(self, event):
        self.is_dragging = False
        # Snap to edge logic could go here
        pos = self.pos()
        if pos.x() < 50: # Snap left
             self.move(0, pos.y())
        
    def show_context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet(self.theme_manager.get_stylesheet())
        
        toggle_action = menu.addAction("Pause" if self.is_active else "Resume")
        toggle_action.triggered.connect(self.toggle_translator.emit)
        
        menu.addSeparator()
        
        settings_action = menu.addAction("Settings")
        settings_action.triggered.connect(self.settings_clicked.emit)
        
        menu.exec_(pos)

    # ==========================================
    # Painting / Visuals
    # ==========================================
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Colors from Theme Manager
        bg_color = QColor(self.theme_manager.get_color("background.elevated")) 
        bg_sec = QColor(self.theme_manager.get_color("background.secondary"))
        text_color = QColor(self.theme_manager.get_color("text.primary"))
        accent = QColor(self.theme_manager.get_color("semantic.accent"))
        success = QColor(self.theme_manager.get_color("semantic.success"))
        error = QColor(self.theme_manager.get_color("semantic.error"))
        
        # Status Color
        base_status = success if self.is_active else QColor("#6b7280")
        
        # Blend with Error if glowing
        if self.error_intensity > 0:
            e_r, e_g, e_b = error.red(), error.green(), error.blue()
            b_r, b_g, b_b = base_status.red(), base_status.green(), base_status.blue()
            
            r = int(b_r * (1 - self.error_intensity) + e_r * self.error_intensity)
            g = int(b_g * (1 - self.error_intensity) + e_g * self.error_intensity)
            b = int(b_b * (1 - self.error_intensity) + e_b * self.error_intensity)
            status_color = QColor(r, g, b)
        else:
            status_color = base_status
        
        # 1. Background (Pill Shape)
        # Gradient
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, bg_color)
        grad.setColorAt(1, bg_sec)
        
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.NoPen)
        
        rect = self.rect()
        radius = 6 if not self.is_expanded else 12
        
        # Draw Left or Right rounded? 
        # If snapped left, round right corners.
        path = QPainterPath()
        path.addRoundedRect(rect.x(), rect.y(), rect.width(), rect.height(), radius, radius)
        painter.drawPath(path)
        
        # 2. Border/Glow (Status)
        if self.is_active or self.error_intensity > 0:
            pen = QPen(status_color)
            width = 2 + (2 * self.error_intensity)
            pen.setWidthF(width)
            painter.setPen(pen)
            painter.drawPath(path)
            
        # 3. Content
        if not self.is_expanded:
            # Idle State: Draw Dots/Status
            painter.setBrush(status_color)
            painter.setPen(Qt.NoPen)
            
            # Draw vertical dots
            cx = self.width() / 2
            cy = self.height() / 2
            painter.drawEllipse(QPoint(int(cx), int(cy)), 3, 3)
            painter.drawEllipse(QPoint(int(cx), int(cy - 12)), 2, 2)
            painter.drawEllipse(QPoint(int(cx), int(cy + 12)), 2, 2)
            
        else:
            # Expanded State: Draw Icons & Text
            painter.setPen(text_color)
            painter.setFont(QFont("Segoe UI", 10, QFont.Bold))
            
            h = self.height()
            w = self.width()
            
            # Section 1: Settings
            r1 = QRect(10, 0, w-20, int(h/3))
            painter.drawText(r1, Qt.AlignVCenter | Qt.AlignLeft, "⚙ Settings")
            
            # Section 2: Toggle
            r2 = QRect(10, int(h/3), w-20, int(h/3))
            icon = "⏸" if self.is_active else "▶"
            label = "Pause" if self.is_active else "Resume"
            painter.drawText(r2, Qt.AlignVCenter | Qt.AlignLeft, f"{icon} {label}")
            
            # Section 3: Status/Source
            r3 = QRect(10, int(2*h/3), w-20, int(h/3))
            painter.setFont(QFont("Segoe UI", 8))
            painter.setPen(QColor(self.theme_manager.get_color("text.secondary")))
            painter.drawText(r3, Qt.AlignVCenter | Qt.AlignLeft, f"via {self.current_source}")

    def glow_error(self):
        """Visual feedback for error: Red transitional glow"""
        self.error_anim = QVariantAnimation(self)
        self.error_anim.setDuration(800)
        self.error_anim.setStartValue(0.0)
        self.error_anim.setKeyValueAt(0.2, 1.0)
        self.error_anim.setKeyValueAt(0.8, 0.5)
        self.error_anim.setEndValue(0.0)
        self.error_anim.valueChanged.connect(self._update_error_glow)
        self.error_anim.start()
        
    def _update_error_glow(self, value):
        self.error_intensity = value
        self.update() 
