"""
Modern Settings Window for MedTranslate Pro
Professional configuration interface with sidebar navigation
Includes History, Favorites, and Advanced Hotkey Recording
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QStackedWidget, 
                               QLabel, QCheckBox, QComboBox, QSpinBox, QLineEdit, QPushButton, 
                               QGroupBox, QScrollArea, QFrame, QListWidgetItem, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QTabWidget, QDialog, QTextEdit, 
                               QMessageBox, QApplication, QSlider)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QFont, QColor, QKeySequence

class HotkeyRecorder(QLineEdit):
    """Widget to record hotkey combinations by pressing them"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Click to record hotkey...")
        self.setReadOnly(True) # Prevent typing
        self.setContextMenuPolicy(Qt.NoContextMenu) # No right click menu
        self.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 6px;
                font-family: Consolas, monospace;
            }
            QLineEdit:focus {
                border: 1px solid #4ade80; /* Green focus border */
                background-color: #1e1e1e;
            }
        """)
        
    def keyPressEvent(self, event):
        """Handle key press to record hotkey"""
        key = event.key()
        modifiers = event.modifiers()
        
        # Ignore standalone modifiers (Control, Shift, Alt, Meta)
        if key in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta):
            return

        # Backspace/Delete to clear
        if key in (Qt.Key_Backspace, Qt.Key_Delete):
            self.clear()
            return
            
        # Build string
        parts = []
        
        if modifiers & Qt.ControlModifier:
            parts.append("ctrl")
        if modifiers & Qt.ShiftModifier:
            parts.append("shift")
        if modifiers & Qt.AltModifier:
            parts.append("alt")
        if modifiers & Qt.MetaModifier:
            parts.append("meta")
            
        # Handle key text
        key_text = QKeySequence(key).toString().lower()
        
        # Fix numeric pad or special keys if needed
        # QKeySequence returns 'Return' for Enter usually, which works for 'keyboard' lib often
        # But 'keyboard' lib prefers specific names.
        
        # Just use the simple string representation for the key
        if not key_text:
            return
            
        parts.append(key_text)
        
        result = "+".join(parts)
        self.setText(result)
        
        # Clear focus to indicate "Done"
        self.clearFocus()

    def focusInEvent(self, event):
        """Visual cue when recording"""
        super().focusInEvent(event)
        self.setPlaceholderText("Press keys now...")
        
    def focusOutEvent(self, event):
        """Reset visual cue"""
        super().focusOutEvent(event)
        self.setPlaceholderText("Click to record hotkey...")


class SettingsWindow(QWidget):
    """Main settings window with sidebar navigation"""
    
    settings_changed = Signal(dict) # Emitted when settings are saved
    
    def __init__(self, config_manager, theme_manager, history_manager):
        super().__init__()
        self.config_manager = config_manager
        self.config = config_manager.config
        self.theme_manager = theme_manager
        self.history_manager = history_manager
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Setup UI layout"""
        self.setWindowTitle("MedTranslate Pro - Settings & History")
        self.resize(1100, 750) 
        
        # Main Layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar (Left)
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(240)
        self.sidebar.setFrameShape(QFrame.NoFrame)
        self.sidebar.setIconSize(QSize(24, 24))
        
        # Sidebar Styling
        bg_color = self.theme_manager.get_color('surface')
        sidebar_bg = self.theme_manager.get_color('bg')
        text_color = self.theme_manager.get_color('text')
        accent_color = self.theme_manager.get_color('accent')
        border_color = self.theme_manager.get_color('border')
        
        self.sidebar.setStyleSheet(f"""
            QListWidget {{
                background-color: {sidebar_bg};
                color: {text_color};
                padding-top: 20px;
                border-right: 1px solid {border_color};
                font-size: 14px;
            }}
            QListWidget::item {{
                height: 55px;
                padding-left: 20px;
                border-left: 4px solid transparent;
            }}
            QListWidget::item:selected {{
                background-color: {bg_color};
                color: {accent_color};
                border-left: 4px solid {accent_color};
                font-weight: bold;
            }}
            QListWidget::item:hover {{
                background-color: {bg_color};
            }}
        """)
        
        # Content Area (Right)
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {bg_color};
            }}
            QLabel {{ color: {text_color}; font-size: 13px; }}
            QCheckBox {{ color: {text_color}; spacing: 8px; font-size: 13px; }}
            QGroupBox {{ 
                color: {accent_color}; 
                font-weight: bold; 
                border: 1px solid {border_color};
                border-radius: 8px;
                margin-top: 14px;
                padding-top: 12px;
                padding-bottom: 12px;
                font-size: 13px;
            }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 5px; }}
            QLineEdit, QComboBox, QSpinBox, QTextEdit {{
                padding: 8px;
                border: 1px solid {border_color};
                border-radius: 6px;
                background-color: {sidebar_bg};
                color: {text_color};
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {{
                border: 1px solid {accent_color};
            }}
            QPushButton {{
                background-color: {accent_color};
                color: {sidebar_bg};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: {self.theme_manager.get_color('success')}; }}
            #secondary_btn {{
                background-color: {sidebar_bg};
                border: 1px solid {border_color};
                color: {text_color};
            }}
            #secondary_btn:hover {{
                background-color: {self.theme_manager.get_color('bg')}; 
                border: 1px solid {accent_color};
            }}
            #danger_btn {{
                background-color: {self.theme_manager.get_color('error')};
                color: white;
            }}
            QTableWidget {{
                background-color: {sidebar_bg};
                color: {text_color};
                gridline-color: {border_color};
                border: 1px solid {border_color};
                border-radius: 6px;
            }}
            QHeaderView::section {{
                background-color: {bg_color};
                color: {text_color};
                padding: 8px;
                border: none;
                font-weight: bold;
            }}
        """)
        
        # Add Pages
        self.add_page("General", "⚙️", self.create_general_page())
        self.add_page("History", "📜", self.create_history_page())
        self.add_page("Translation", "🌐", self.create_translation_page())
        self.add_page("Appearance", "🎨", self.create_appearance_page())
        self.add_page("Hotkeys", "⌨️", self.create_hotkeys_page())
        self.add_page("AI Settings", "🤖", self.create_ai_page())
        self.add_page("About", "ℹ️", self.create_about_page())
        
        self.sidebar.currentRowChanged.connect(self.content_area.setCurrentIndex)
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area)
        self.sidebar.setCurrentRow(0)

    def add_page(self, title, icon_text, widget):
        item = QListWidgetItem(f" {icon_text}  {title}")
        self.sidebar.addItem(item)
        if title == "History":
            self.content_area.addWidget(widget)
        else:
            scroll = QScrollArea()
            scroll.setWidget(widget)
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.NoFrame)
            self.content_area.addWidget(scroll)

    # --- Pages ---
    
    def create_general_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        
        # Header
        self._add_header(layout, "General Settings")
        
        grp_startup = QGroupBox("Startup & Behavior")
        vbox = QVBoxLayout()
        self.chk_autostart = QCheckBox("Start with Windows")
        self.chk_notifications = QCheckBox("Show Notifications")
        self.chk_sound = QCheckBox("Play Sound on Translation")
        vbox.addWidget(self.chk_autostart)
        vbox.addWidget(self.chk_notifications)
        vbox.addWidget(self.chk_sound)
        grp_startup.setLayout(vbox)
        layout.addWidget(grp_startup)
        
        layout.addStretch()
        self._add_action_buttons(layout)
        return page

    def create_history_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with Search
        header = QHBoxLayout()
        title = QLabel("Translation History")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.addWidget(title)
        header.addStretch()
        
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Search history...")
        self.txt_search.setFixedWidth(250)
        self.txt_search.textChanged.connect(self.search_history)
        header.addWidget(self.txt_search)
        
        btn_clear = QPushButton("Clear All")
        btn_clear.setObjectName("danger_btn")
        btn_clear.setFixedWidth(100)
        btn_clear.clicked.connect(self.clear_history)
        header.addWidget(btn_clear)
        
        layout.addLayout(header)
        layout.addWidget(QLabel("Double-click any row to view full text details. Data is stored locally."))
        
        # Tabs
        tabs = QTabWidget()
        self.table_history = self.create_history_table(self.history_manager.get_history(500))
        tabs.addTab(self.table_history, "Recent Translations")
        
        self.table_favorites = self.create_history_table(self.history_manager.get_favorites())
        tabs.addTab(self.table_favorites, "Favorites ❤️")
        
        layout.addWidget(tabs)
        layout.addWidget(QPushButton("Refresh Data", objectName="secondary_btn", clicked=lambda: self.refresh_tables(tabs)))
        return page

    def create_history_table(self, data):
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Original Text", "Translation", "Source"])
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        table.setColumnWidth(0, 300) 
        
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setWordWrap(True)
        table.verticalHeader().setDefaultSectionSize(60)
        table.doubleClicked.connect(self.show_history_detail)
        
        self.populate_table(table, data)
        return table

    def populate_table(self, table, data):
        table.setRowCount(0)
        for i, entry in enumerate(data):
            table.insertRow(i)
            orig = QTableWidgetItem(entry.get('original', ''))
            orig.setToolTip(entry.get('original', ''))
            table.setItem(i, 0, orig)
            
            trans = QTableWidgetItem(entry.get('translation', ''))
            trans.setToolTip(entry.get('translation', ''))
            table.setItem(i, 1, trans)
            
            source = QTableWidgetItem(entry.get('source', ''))
            table.setItem(i, 2, source)
    
    def show_history_detail(self, index):
        table = self.sender()
        row = index.row()
        original = table.item(row, 0).text()
        translation = table.item(row, 1).text()
        source = table.item(row, 2).text()
        
        dlg = QDialog(self)
        dlg.setWindowTitle("Translation Details")
        dlg.resize(600, 450)
        lay = QVBoxLayout(dlg)
        
        lay.addWidget(QLabel("Original Text:"))
        txt_orig = QTextEdit()
        txt_orig.setPlainText(original)
        txt_orig.setReadOnly(True)
        lay.addWidget(txt_orig)
        
        lay.addWidget(QLabel("Translation:"))
        txt_trans = QTextEdit()
        txt_trans.setPlainText(translation)
        txt_trans.setReadOnly(True)
        lay.addWidget(txt_trans)
        
        lay.addWidget(QLabel(f"Source: {source}"))
        btn_cls = QPushButton("Close")
        btn_cls.clicked.connect(dlg.close)
        lay.addWidget(btn_cls)
        dlg.exec()

    def search_history(self, text):
        pass # Search logic could be added here similar to populate_table logic

    def clear_history(self):
        reply = QMessageBox.question(self, 'Clear History', "Are you sure you want to delete ALL translation history?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.history_manager.clear_history()
            self.refresh_tables()

    def refresh_tables(self, tabs=None):
        if hasattr(self, 'table_history'):
            self.populate_table(self.table_history, self.history_manager.get_history(500))
        if hasattr(self, 'table_favorites'):
            self.populate_table(self.table_favorites, self.history_manager.get_favorites())

    def create_translation_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self._add_header(layout, "Translation Settings")
        
        grp_source = QGroupBox("Method & Priority")
        vbox = QVBoxLayout()
        self.combo_source = QComboBox()
        self.combo_source.addItems(["Auto (Smart Detection)", "Local Dictionary", "LibreTranslate (Online)", "OpenRouter AI", "Keyboard Fixer"])
        vbox.addWidget(QLabel("Preferred translation method:"))
        vbox.addWidget(self.combo_source)
        grp_source.setLayout(vbox)
        layout.addWidget(grp_source)
        
        grp_cache = QGroupBox("Performance & Caching")
        vbox2 = QVBoxLayout()
        self.chk_cache = QCheckBox("Enable Caching (Faster generic results)")
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Cache entries:"))
        self.spin_cache = QSpinBox()
        self.spin_cache.setRange(0, 50000)
        hbox.addWidget(self.spin_cache)
        vbox2.addWidget(self.chk_cache)
        vbox2.addLayout(hbox)
        grp_cache.setLayout(vbox2)
        layout.addWidget(grp_cache)
        
        grp_fallback = QGroupBox("Reliability")
        vbox3 = QVBoxLayout()
        self.chk_fallback = QCheckBox("Offline Fallback (Use Local Dictionary if Online fails)")
        vbox3.addWidget(self.chk_fallback)
        grp_fallback.setLayout(vbox3)
        layout.addWidget(grp_fallback)
        
        layout.addStretch()
        self._add_action_buttons(layout)
        return page

    def create_appearance_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self._add_header(layout, "Appearance")
        
        grp_theme = QGroupBox("Theme & Style")
        vbox = QVBoxLayout()
        self.combo_theme = QComboBox()
        
        # Dynamic Theme Loading
        self.theme_map = {}
        themes = self.theme_manager.themes
        
        for key in sorted(themes.keys()):
            name = themes[key].get('name', key.title())
            self.theme_map[name] = key
            self.combo_theme.addItem(name)
            
        self.combo_theme.currentIndexChanged.connect(self.apply_theme_preview)
        vbox.addWidget(QLabel("Application Theme:"))
        vbox.addWidget(self.combo_theme)
        grp_theme.setLayout(vbox)
        layout.addWidget(grp_theme)
        
        # Floating Tab Settings
        grp_floating = QGroupBox("Floating Tab Style")
        vbox_f = QVBoxLayout()
        
        # Height
        hbox_h = QHBoxLayout()
        hbox_h.addWidget(QLabel("Height (Length):"))
        self.slider_tab_height = QSlider(Qt.Horizontal)
        self.slider_tab_height.setRange(50, 400)
        hbox_h.addWidget(self.slider_tab_height)
        self.spin_tab_height = QSpinBox()
        self.spin_tab_height.setRange(50, 400)
        self.slider_tab_height.valueChanged.connect(self.spin_tab_height.setValue)
        self.spin_tab_height.valueChanged.connect(self.slider_tab_height.setValue)
        hbox_h.addWidget(self.spin_tab_height)
        vbox_f.addLayout(hbox_h)
        
        # Hover Width
        hbox_w = QHBoxLayout()
        hbox_w.addWidget(QLabel("Expanded Width:"))
        self.slider_tab_width = QSlider(Qt.Horizontal)
        self.slider_tab_width.setRange(60, 300)
        hbox_w.addWidget(self.slider_tab_width)
        self.spin_tab_width = QSpinBox()
        self.spin_tab_width.setRange(60, 300)
        self.slider_tab_width.valueChanged.connect(self.spin_tab_width.setValue)
        self.spin_tab_width.valueChanged.connect(self.slider_tab_width.setValue)
        hbox_w.addWidget(self.spin_tab_width)
        vbox_f.addLayout(hbox_w)
        
        # Y Position
        hbox_y = QHBoxLayout()
        hbox_y.addWidget(QLabel("Vertical Position (Y):"))
        self.spin_tab_y = QSpinBox()
        self.spin_tab_y.setRange(0, 2000)
        hbox_y.addWidget(self.spin_tab_y)
        vbox_f.addLayout(hbox_y)
        
        grp_floating.setLayout(vbox_f)
        layout.addWidget(grp_floating)
        
        grp_popup = QGroupBox("Popup Window")
        vbox2 = QVBoxLayout()
        
        grid = QVBoxLayout() # Nested
        hbox_p = QHBoxLayout()
        hbox_p.addWidget(QLabel("Default Position:"))
        self.combo_position = QComboBox()
        self.combo_position.addItems(["Top Right", "Top Left", "Bottom Right", "Bottom Left", "Center"])
        hbox_p.addWidget(self.combo_position)
        grid.addLayout(hbox_p)
        
        hbox_o = QHBoxLayout()
        hbox_o.addWidget(QLabel("Opacity (%):"))
        self.spin_opacity = QSpinBox()
        self.spin_opacity.setRange(20, 100)
        hbox_o.addWidget(self.spin_opacity)
        grid.addLayout(hbox_o)
        
        self.chk_autoclose = QCheckBox("Auto-close popup after delay")
        hbox_d = QHBoxLayout()
        hbox_d.addWidget(QLabel("Close Delay (seconds):"))
        self.spin_delay = QSpinBox()
        self.spin_delay.setRange(1, 60)
        hbox_d.addWidget(self.spin_delay)
        
        vbox2.addLayout(grid)
        vbox2.addWidget(self.chk_autoclose)
        vbox2.addLayout(hbox_d)
        
        # Advanced Popup Behavior
        vbox2.addWidget(QLabel("Advanced Behavior:"))
        self.chk_ctrl_close = QCheckBox("Close on 'Ctrl' Key Press")
        self.chk_outside_close = QCheckBox("Close on Click Outside")
        vbox2.addWidget(self.chk_ctrl_close)
        vbox2.addWidget(self.chk_outside_close)
        
        grp_popup.setLayout(vbox2)
        layout.addWidget(grp_popup)
        
        layout.addStretch()
        self._add_action_buttons(layout)
        return page

    def create_hotkeys_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self._add_header(layout, "Keyboard Shortcuts")
        
        grp_hotkeys = QGroupBox("Global Hotkeys")
        layout_grid = QVBoxLayout()
        layout_grid.setSpacing(10)
        self.hotkey_inputs = {}
        
        hotkey_labels = {
            "start_translator": "Activate Translator",
            "stop_translator": "Deactivate Translator",
            "copy_result": "Copy Result",
            "pin_window": "Pin Window",
            "open_settings": "Open Settings",
            "force_ai": "Force AI Translation",
            "force_libre": "Force LibreTranslate",
            "force_local": "Force Local Dictionary",
            "force_keyfix": "Force Keyboard Fixer"
        }
        
        for key, label in hotkey_labels.items():
            hbox = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setFixedWidth(200)
            hbox.addWidget(lbl)
            
            # Use specific recorder widget
            recorder = HotkeyRecorder()
            self.hotkey_inputs[key] = recorder
            hbox.addWidget(recorder)
            layout_grid.addLayout(hbox)
            
        grp_hotkeys.setLayout(layout_grid)
        layout.addWidget(grp_hotkeys)
        layout.addWidget(QLabel("* Click box and press keys to record. Backspace to clear."))
        
        layout.addStretch()
        self._add_action_buttons(layout)
        return page

    def create_ai_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self._add_header(layout, "AI Configuration")
        
        grp_api = QGroupBox("OpenRouter API")
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("API Key:"))
        self.txt_apikey = QLineEdit()
        self.txt_apikey.setEchoMode(QLineEdit.Password)
        self.txt_apikey.setPlaceholderText("sk-or-v1-...")
        vbox.addWidget(self.txt_apikey)
        vbox.addWidget(QLabel("Model:"))
        self.txt_model = QLineEdit()
        self.txt_model.setPlaceholderText("e.g. google/gemini-2.0-flash-exp:free")
        vbox.addWidget(self.txt_model)
        grp_api.setLayout(vbox)
        layout.addWidget(grp_api)
        
        grp_prompt = QGroupBox("System Prompt")
        vbox2 = QVBoxLayout()
        vbox2.addWidget(QLabel("Instructions for the AI (Behavior, style, length):"))
        self.txt_prompt = QTextEdit()
        self.txt_prompt.setFixedHeight(120)
        vbox2.addWidget(self.txt_prompt)
        grp_prompt.setLayout(vbox2)
        layout.addWidget(grp_prompt)
        
        layout.addStretch()
        self._add_action_buttons(layout)
        return page
        
    def create_about_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        logo = QLabel("🏥")
        logo.setFont(QFont("Segoe UI", 80))
        logo.setAlignment(Qt.AlignCenter)
        title = QLabel("MedTranslate Pro")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setStyleSheet(f"color: {self.theme_manager.get_color('accent')}")
        title.setAlignment(Qt.AlignCenter)
        ver = QLabel("Version 1.2.0")
        ver.setFont(QFont("Segoe UI", 14))
        ver.setStyleSheet(f"color: {self.theme_manager.get_color('text_secondary')}")
        ver.setAlignment(Qt.AlignCenter)
        desc = QLabel("Medical Translation Assistant\nDeveloped by Raafat Reda")
        desc.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addWidget(ver)
        layout.addWidget(desc)
        layout.addStretch()
        
        # Reset Button
        btn_reset = QPushButton("Reset All Settings to Default")
        btn_reset.setObjectName("danger_btn")
        btn_reset.setFixedWidth(250)
        btn_reset.clicked.connect(self.reset_to_default)
        layout.addWidget(btn_reset, alignment=Qt.AlignCenter)
        
        layout.addSpacing(10)
        
        btn_exit_app = QPushButton("Exit Application")
        btn_exit_app.setObjectName("danger_btn")
        btn_exit_app.setFixedWidth(200)
        btn_exit_app.clicked.connect(self.quit_app)
        layout.addWidget(btn_exit_app, alignment=Qt.AlignCenter)
        
        return page
    
    def _add_header(self, layout, text):
        title = QLabel(text)
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet(f"color: {self.theme_manager.get_color('accent')}; margin-bottom: 10px;")
        layout.addWidget(title)
        
    def _add_action_buttons(self, layout):
        hbox = QHBoxLayout()
        hbox.addStretch()
        
        btn_apply = QPushButton("Apply")
        btn_apply.setObjectName("secondary_btn")
        btn_apply.clicked.connect(self.apply_settings)
        btn_apply.setFixedWidth(100)
        
        btn_save = QPushButton("Save & Close")
        btn_save.clicked.connect(self.save_settings)
        btn_save.setFixedWidth(120)
        
        hbox.addWidget(btn_apply)
        hbox.addWidget(btn_save)
        layout.addLayout(hbox)

    def load_settings(self):
        c = self.config
        self.chk_autostart.setChecked(c.get('general', {}).get('auto_start', False))
        self.chk_notifications.setChecked(c.get('general', {}).get('show_notifications', True))
        self.chk_sound.setChecked(c.get('general', {}).get('play_sound', False))
        
        src_map = {"auto": 0, "local": 1, "libre": 2, "openrouter_ai": 3, "keyboard_fixer": 4}
        active = c.get('translation', {}).get('active_source', 'auto')
        self.combo_source.setCurrentIndex(src_map.get(active, 0))
        
        self.chk_cache.setChecked(c.get('translation', {}).get('cache_enabled', True))
        self.spin_cache.setValue(c.get('translation', {}).get('cache_size', 100))
        self.chk_fallback.setChecked(c.get('translation', {}).get('offline_fallback', True))
        
        # Dynamic Themes
        theme_id = c.get('appearance', {}).get('theme', 'dark_minimal')
        index = 0
        if hasattr(self, 'theme_map'):
             # Find index for this ID
             for i in range(self.combo_theme.count()):
                 name = self.combo_theme.itemText(i)
                 if self.theme_map.get(name) == theme_id:
                     index = i
                     break
        self.combo_theme.setCurrentIndex(index)
        
        # Floating Tab Settings
        ft = c.get('floating_tab', {})
        self.slider_tab_height.setValue(ft.get('height', 100))
        self.slider_tab_width.setValue(ft.get('width_expanded', 85))
        self.spin_tab_y.setValue(ft.get('position_y', 150))
        
        pos_map = {"top_right": 0, "top_left": 1, "bottom_right": 2, "bottom_left": 3, "center": 4}
        pos = c.get('popup', {}).get('position', 'top_right')
        self.combo_position.setCurrentIndex(pos_map.get(pos, 0))
        self.spin_opacity.setValue(c.get('popup', {}).get('opacity', 95))
        self.chk_autoclose.setChecked(c.get('popup', {}).get('auto_close', True))
        self.spin_delay.setValue(c.get('popup', {}).get('auto_close_delay', 5))
        
        # New Settings (Removed Always Pin)
        self.chk_ctrl_close.setChecked(c.get('popup', {}).get('close_on_ctrl_click', True))
        self.chk_outside_close.setChecked(c.get('popup', {}).get('close_on_outside_click', False))
        
        hotkeys = c.get('hotkeys', {})
        for key, edit in self.hotkey_inputs.items():
            edit.setText(hotkeys.get(key, ""))
            
        self.txt_apikey.setText(c.get('openrouter', {}).get('api_key', ''))
        self.txt_model.setText(c.get('openrouter', {}).get('model', 'amazon/nova-2-lite-v1:free'))
        
        # Explicit check for system prompt
        prompt = c.get('openrouter', {}).get('system_prompt', '')
        self.txt_prompt.setPlainText(prompt)

    def _collect_settings(self):
        """Collect current UI state into config dict"""
        c = self.config
        c['general']['auto_start'] = self.chk_autostart.isChecked()
        c['general']['show_notifications'] = self.chk_notifications.isChecked()
        c['general']['play_sound'] = self.chk_sound.isChecked()
        
        src_map_rev = {0: "auto", 1: "local", 2: "libre", 3: "openrouter_ai", 4: "keyboard_fixer"}
        c['translation']['active_source'] = src_map_rev[self.combo_source.currentIndex()]
        c['translation']['cache_enabled'] = self.chk_cache.isChecked()
        c['translation']['cache_size'] = self.spin_cache.value()
        c['translation']['offline_fallback'] = self.chk_fallback.isChecked()
        
        # Dynamic Themes
        name = self.combo_theme.currentText()
        if hasattr(self, 'theme_map'):
            c['appearance']['theme'] = self.theme_map.get(name, 'dark_minimal')
        else:
            c['appearance']['theme'] = 'dark_minimal'
        
        # Floating Tab Settings
        if 'floating_tab' not in c: c['floating_tab'] = {}
        c['floating_tab']['height'] = self.slider_tab_height.value()
        c['floating_tab']['width_expanded'] = self.slider_tab_width.value()
        c['floating_tab']['position_y'] = self.spin_tab_y.value()
        
        pos_map_rev = {0: "top_right", 1: "top_left", 2: "bottom_right", 3: "bottom_left", 4: "center"}
        c['popup']['position'] = pos_map_rev[self.combo_position.currentIndex()]
        c['popup']['opacity'] = self.spin_opacity.value()
        c['popup']['auto_close'] = self.chk_autoclose.isChecked()
        c['popup']['auto_close_delay'] = self.spin_delay.value()
        
        # New Settings (Removed Always Pin)
        c['popup']['close_on_ctrl_click'] = self.chk_ctrl_close.isChecked()
        c['popup']['close_on_outside_click'] = self.chk_outside_close.isChecked()
        
        for key, edit in self.hotkey_inputs.items():
            if edit.text().strip():
                c['hotkeys'][key] = edit.text().strip()
                
        c['openrouter']['api_key'] = self.txt_apikey.text().strip()
        c['openrouter']['model'] = self.txt_model.text().strip()
        
        # CRITICAL FIX: Ensure prompt is captured
        c['openrouter']['system_prompt'] = self.txt_prompt.toPlainText()
        
        return c

    def apply_settings(self):
        c = self._collect_settings()
        self.config_manager.save_config() # Persist to disk
        self.settings_changed.emit(c)     # Notify app
        QMessageBox.information(self, "Settings Applied", "Settings have been applied successfully.")
        
    def reset_to_default(self):
        reply = QMessageBox.question(self, 'Reset Settings', 
                                   "Are you sure you want to reset ALL settings to default? usage data will be kept.",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            import os
            # We can use ConfigManager default config
            defaults = self.config_manager.DEFAULT_CONFIG.copy()
            # Preserve some things if needed? No, user said reset to default.
            # Maybe preserve API key? "Reset All" usually implies everything.
            # I will preserve API Key as it is painful to retype.
            current_key = self.config['openrouter']['api_key']
            defaults['openrouter']['api_key'] = current_key
            
            self.config = defaults
            self.config_manager.config = defaults
            self.config_manager.save_config()
            self.load_settings() # Reload UI
            self.settings_changed.emit(defaults)
            QMessageBox.information(self, "Reset Complete", "Settings have been reset to default values.")

    def save_settings(self):
        c = self._collect_settings()
        self.config_manager.save_config()
        self.settings_changed.emit(c)
        self.close()

    def apply_theme_preview(self):
        name = self.combo_theme.currentText()
        if hasattr(self, 'theme_map'):
             tid = self.theme_map.get(name, 'dark_minimal')
             self.theme_manager.set_theme(tid)
        
    def quit_app(self):
        reply = QMessageBox.question(self, 'Exit Application', "Are you sure you want to quit MedTranslate Pro?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            QApplication.quit()
