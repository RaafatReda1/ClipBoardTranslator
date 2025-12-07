# 🏥 MedTranslate Pro

**A powerful, lightweight desktop application for instant medical term translation and explanation.**

## 🎯 Overview

MedTranslate Pro is an always-running desktop assistant designed for medical students and professionals who need quick, reliable translations while studying or working. It automatically captures copied text and provides instant translations through multiple intelligent sources.

## ✨ Key Features

### 🔄 **4 Translation Sources**
1. **Keyboard Layout Fixer** ⌨️ - Automatically detects and fixes text typed in wrong keyboard layout
2. **Local Dictionary** 📚 - 87,000+ medical terms for instant offline translation
3. **LibreTranslate** 🌐 - Free online translation service
4. **OpenRouter AI** 🤖 - Detailed medical term explanations using AI

### 🎨 **Modern UI**
- **System Tray Application** - Runs silently in background
- **Floating Access Tab** - Quick access to settings
- **Translation Popup** - Beautiful, non-intrusive results window
- **5 Built-in Themes** - Dark Minimal, Light Clean, Medical Blue, Forest, Sunset

### ⚡ **Smart Features**
- **Auto-Detection** - Intelligently chooses best translation source
- **Caching** - Lightning-fast repeated lookups
- **Offline Mode** - Works without internet using local dictionary
- **Global Hotkeys** - Control everything with keyboard shortcuts
- **RTL Support** - Perfect Arabic text rendering

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- Windows 10/11 (primary target)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/RaafatReda1/ClipBoardTranslator.git
cd ClipBoardTranslator
```

2. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API Key (Optional - for AI features)**
```bash
# Copy the template config file
copy config.template.json config.json

# Edit config.json and add your OpenRouter API key
# Get a free API key from: https://openrouter.ai/
```

**Note:** The app works perfectly without an API key using the other 3 translation sources!

5. **Run the application**
```bash
python main.py
```

## 🎮 Usage

### Quick Start
1. Launch MedTranslate Pro
2. Press `Ctrl+Shift+1` to activate translator
3. Copy any medical term
4. Translation appears automatically!

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Start Translator | `Ctrl+Shift+1` |
| Stop Translator | `Ctrl+Shift+2` |
| Cycle Sources | `Ctrl+Shift+3` |
| Force AI | `Ctrl+Shift+A` |
| Force LibreTranslate | `Ctrl+Shift+L` |
| Force Local Dict | `Ctrl+Shift+D` |
| Force Keyboard Fix | `Ctrl+Shift+K` |
| Copy Result | `Ctrl+Alt+C` |
| Pin Window | `Ctrl+Alt+P` |
| Open Settings | `Ctrl+Alt+S` |

## 🏗️ Project Structure

```
MedTranslatePro/
│
├── main.py                          # Entry point
├── requirements.txt                 # Dependencies
├── config.json                      # User settings (auto-generated)
├── README.md                        # This file
│
├── core/                            # Core functionality
│   ├── clipboard_monitor.py         # Monitors clipboard changes
│   ├── translation_engine.py        # Main translation coordinator
│   ├── keyboard_fixer.py            # Layout correction logic
│   ├── local_dictionary.py          # Offline dictionary
│   ├── libre_translator.py          # LibreTranslate integration
│   ├── openrouter_ai.py             # OpenRouter API integration
│   └── hotkey_manager.py            # Global hotkey handling
│
├── ui/                              # User interface
│   ├── system_tray.py               # System tray icon & menu
│   ├── floating_tab.py              # Collapsible side tab
│   ├── popup_window.py              # Translation result popup
│   ├── settings_window.py           # Settings dialog
│   └── theme_manager.py             # Theme/styling system
│
├── utils/                           # Utilities
│   ├── config_manager.py            # Save/load settings
│   ├── cache_manager.py             # Translation caching
│   └── logger.py                    # Error logging
│
└── resources/                       # Resources
    ├── icons/                       # Application icons
    ├── themes/                      # Color themes
    │   └── default_themes.json      # Built-in themes
    └── dictionaries/                # Offline dictionaries
        └── dictionary.json          # 87,000+ medical terms
```

## ⚙️ Configuration

The application creates a `config.json` file with all settings. You can customize:

- **Translation Sources** - Choose active source and priority order
- **OpenRouter AI** - Configure API key, model, and prompts
- **Hotkeys** - Customize all keyboard shortcuts
- **Appearance** - Select theme and customize colors
- **Popup Behavior** - Auto-close delay, position, animations
- **Advanced** - Network timeout, caching, logging

## 🎨 Themes

### Built-in Themes
1. **Dark Minimal** - Professional dark theme (default)
2. **Light Clean** - Clean light theme
3. **Medical Blue** - Medical-inspired blue palette
4. **Forest** - Warm earth tones
5. **Sunset** - Vibrant purple and gold

### Custom Themes
You can create custom themes by editing `resources/themes/default_themes.json`

## 🔧 Development

### Current Status ✅
- [x] Project structure created
- [x] Configuration manager
- [x] Cache manager
- [x] Logger utility
- [x] Keyboard layout fixer
- [x] Local dictionary handler
- [x] LibreTranslate integration
- [x] OpenRouter AI integration
- [x] Translation engine
- [x] Clipboard monitor
- [x] Hotkey manager
- [x] Theme system

### In Progress 🚧
- [ ] System tray UI
- [ ] Floating tab UI
- [ ] Translation popup window
- [ ] Settings window (6 tabs)
- [ ] Main application entry point
- [ ] Testing and debugging

### Planned Features 🎯
- [ ] History panel
- [ ] Favorites system
- [ ] Export translations
- [ ] Voice output (TTS)
- [ ] Statistics tracking
- [ ] Auto-start with Windows

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.

## 👤 Author

**Raafat Reda**
- Email: rafat2782005@gmail.com
- Phone: 01022779263
- GitHub: [@RaafatReda1](https://github.com/RaafatReda1)

## 🙏 Acknowledgments

- **OpenRouter** - For providing free AI API access
- **LibreTranslate** - For open-source translation
- **PySide6** - For the modern Qt6 framework
- All contributors and users!

## 📊 Statistics

- **87,425** medical terms in local dictionary
- **4** translation sources
- **5** built-in themes
- **12** customizable hotkeys
- **100** cached translations (configurable)

---

**Made with ❤️ for medical students and professionals**
