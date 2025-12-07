# 🛠️ MedTranslate Pro - Settings Window Documentation

## 1. Architectural Overview
The **Settings Window** (`ui/settings_window.py`) is the central control hub of the application. It is built using **PySide6 (Qt for Python)** and employs a modular, event-driven architecture to manage configuration, visual styling, and application behavior.

### **Core Techniques Used:**
*   **JSON-based Persistence**: All settings are serialized to `config.json` via the `ConfigManager`. This ensures state values (checkboxes, text fields) persist across restarts.
*   **Signal-Slot Mechanism**: The window emits a custom `settings_changed` signal whenever "Apply" or "Save" is clicked. This signal carries the updated configuration dictionary, which `main.py` intercepts to update all active components (Translation Engine, Popup, Floating Tab) in real-time.
*   **Dynamic UI Construction**: The Settings Window uses a `QListWidget` sidebar alongside a `QStackedWidget` to create a modern, paginated interface without spawning multiple windows.

---

## 2. Tab-by-Tab Technical Breakdown

### 🌍 **Tab 1: Translation Settings**
Controls the logic of the `TranslationEngine`.

*   **Preferred Translation Method**:
    *   *Control*: `QComboBox`.
    *   *Logic*: Maps friendly names ("Auto", "Local Dictionary") to internal IDs (`auto`, `local`, `libre`, `openrouter_ai`).
    *   *Technique*: The system uses a **Priority Chain**. If "Auto" is selected, it tries sources in order: `Keyboard Fixer -> OpenRouter AI -> LibreTranslate -> Local Dictionary`.
*   **Performance & Caching**:
    *   *Controls*: `QCheckBox` (Enable), `QSpinBox` (Size).
    *   *Technique*: Implements an **LRU (Least Recently Used) Cache**. Storing 100-5000 entries allows instant retrieval of previous translations without network calls.
*   **Reliability (Fallback)**:
    *   *Control*: `QCheckBox`.
    *   *Logic*: If an online source (AI/Libre) fails, the system automatically falls back to the embedded `LocalDictionary`.

### 🎨 **Tab 2: Appearance**
Manages the visual identity and window behaviors.

*   **Theme & Style**:
    *   *Control*: `QComboBox` (Dark Minimal / Light Clean).
    *   *Technique*: **Instant Apply**. Connecting `currentIndexChanged` to `apply_theme_preview` triggers a global repaint immediately, updating CSS stylesheets (`setStyleSheet`) across the entire app without needing a save.
*   **Floating Tab Style** (New):
    *   *Controls*: `QSlider` + `QSpinBox` pairs (synchronized).
    *   *Logic*: Configures the **Idle State** (minimized) and **Hover State** (expanded) dimensions of the floating sidebar.
    *   *Technique*: **Dual-Control Synchronization**. Moving the slider updates the number box, and vice versa, providing both precision and ease of use.
*   **Popup Window**:
    *   *Controls*: Opacity (`QSpinBox`, 20-100%), Position, Auto-Close Timer.
    *   *Advanced Behavior*:
        *   **Close on 'Ctrl' Key**: Uses `keyPressEvent` interception.
        *   **Close upon Click Outside**: Uses `focusOutEvent` detection.
        *   *Pinning*: Bypasses the auto-close timer but still respects manual close triggers if configured.

### ⌨️ **Tab 3: Keyboard Shortcuts**
Manages global hotkeys using a custom widget.

*   **Hotkey Recorder**:
    *   *Tech Stack*: Custom `QLineEdit` subclass (`HotkeyRecorder`).
    *   *Technique*: **Event Interception**.
        *   It overrides `keyPressEvent`.
        *   Instead of typing text, it captures the `QKeyEvent`.
        *   It transforms the key code + modifiers (Ctrl, Alt, Shift) into a string string (e.g., "Ctrl+Alt+T") using `QKeySequence`.
        *   It prevents standard typing and only accepts valid key combinations.

### 🤖 **Tab 4: AI Configuration**
Settings for the `OpenRouterAI` integration.

*   **API Key & Model**:
    *   *Control*: `QLineEdit` (Password echo mode for security).
    *   *Logic*: Stores credentials for accessing LLMs (like Llama 3, Gemini, etc.).
*   **System Prompt**:
    *   *Control*: `QTextEdit`.
    *   *Technique*: **Prompt Engineering**. This text is injected as the "System Message" context in every API call, allowing you to define the AI's personality (e.g., "You are a medical expert...").

### 📜 **Tab 5: Recent Translations (History)**
A database viewer for stored translations.

*   **Data View**:
    *   *Control*: `QTableWidget`.
    *   *Layout*: Columns for Original, Translation, and Source.
    *   *Technique*: **Virtualization**. Loads the last 500 entries from `history.json`.
*   **Interaction**:
    *   *Double-Click*: Opens a modal `QDialog` showing the full text, useful for long paragraphs that are truncated in the table view.
*   **Favorites**:
    *   *Logic*: Filters the history list to show only items marked with `is_favorite=True`.

### ℹ️ **Tab 6: About**
Application metadata and critical resets.

*   **Reset All Settings**:
    *   *Control*: `QPushButton`.
    *   *Logic*:
        1.  Loads the hardcoded `DEFAULT_CONFIG`.
        2.  **Preserves** sensitive data (API Key) by reading it from the current config before overwriting.
        3.  Saves to disk and reloads the UI.

---

## 3. Data Flow Update Cycle

1.  **User Interaction**: User changes a slider or checkbox.
2.  **Collection**: `_collect_settings()` method scrapes values from all widgets into a Python dictionary.
3.  **Persistence**: `ConfigManager.save_config()` writes this dictionary to `config.json`.
4.  **Propagation**:
    *   `settings_changed` signal is emitted.
    *   `main.py` receives the signal.
    *   `main.py` calls `update_config()` on `FloatingTab` and `TranslationEngine`.
    *   `main.py` updates the attributes of `TranslationPopup`.
5.  **Result**: The application behavior changes instantly without a restart.
