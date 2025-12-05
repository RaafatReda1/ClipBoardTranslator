import os
import json
import pyperclip
import time
import re
import threading
import keyboard
from tkinter import Tk, Label, Frame, Button, Toplevel, Radiobutton, StringVar, Text, DISABLED, CENTER
from PIL import Image, ImageTk
from difflib import get_close_matches
import sys
import subprocess
import tempfile

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Global variables reation
translator_active = False
current_translation = ""
activate_key = "ctrl+shift+1"
deactivate_key = "ctrl+shift+2"
copy_key = "ctrl+alt+c"
current_dictionary_type = "translations"  # Default to translations dictionary
padding = 10  # or any value you prefer, e.g., 20

# Color palettes
color_palettes = {
    "Primary": {
        "bg": "#282A36",
        "border": "#50FA7B",
        "text_fg": "#FF79C6",
        "translation_fg": "#8BE9FD",
        "translated_text_fg": "#F1FA8C",
        "button_bg": "#50FA7B",
        "button_fg": "#282A36",
        "button_active_bg": "#69FF94",
        "button_active_fg": "#282A36"
    },
    "Ocean Breeze": {
        "bg": "#003B46",
        "border": "#07575B",
        "text_fg": "#C4DFE6",
        "translation_fg": "#66A5AD",
        "translated_text_fg": "#FFCCBC",
        "button_bg": "#66A5AD",
        "button_fg": "#003B46",
        "button_active_bg": "#C4DFE6",
        "button_active_fg": "#003B46"
    },
    "Sunset": {
        "bg": "#2E1A47",
        "border": "#FF6F61",
        "text_fg": "#FFD700",
        "translation_fg": "#FDEBD0",
        "translated_text_fg": "#FFB6C1",
        "button_bg": "#FF6F61",
        "button_fg": "#2E1A47",
        "button_active_bg": "#FFD700",
        "button_active_fg": "#2E1A47"
    },
    "Forest": {
        "bg": "#264653",
        "border": "#2A9D8F",
        "text_fg": "#E9C46A",
        "translation_fg": "#F4A261",
        "translated_text_fg": "#E76F51",
        "button_bg": "#2A9D8F",
        "button_fg": "#264653",
        "button_active_bg": "#E9C46A",
        "button_active_fg": "#264653"
    },
    "Candy Pop": {
        "bg": "#FFF5E1",
        "border": "#FF6F91",
        "text_fg": "#FF9671",
        "translation_fg": "#FFC75F",
        "translated_text_fg": "#845EC2",
        "button_bg": "#FF6F91",
        "button_fg": "#FFF5E1",
        "button_active_bg": "#FFC75F",
        "button_active_fg": "#845EC2"
    },
    "Lime Splash": {
        "bg": "#E6FFB3",
        "border": "#9AE66E",
        "text_fg": "#79D70F",
        "translation_fg": "#FFD93D",
        "translated_text_fg": "#EE6C4D",
        "button_bg": "#9AE66E",
        "button_fg": "#E6FFB3",
        "button_active_bg": "#FFD93D",
        "button_active_fg": "#E6FFB3"
    },
    "Sky Daylight": {
        "bg": "#000",
        "border": "#4DD0E1",
        "text_fg": "#00ACC1",
        "translation_fg": "#80DEEA",
        "translated_text_fg": "#FFD93D",
        "button_bg": "#4DD0E1",
        "button_fg": "#E0F7FA",
        "button_active_bg": "#00ACC1",
        "button_active_fg": "#E0F7FA"
    }
}
# Config file path
config_path = resource_path("config.json")

# Load palette from config
def load_saved_palette():
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                palette_name = config.get("palette")
                if palette_name in color_palettes:
                    return color_palettes[palette_name]
        except:
            pass
    return color_palettes["Primary"]

# Save palette to config
def save_palette(name):
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump({"palette": name}, f)

# Initialize current_palette
current_palette = load_saved_palette()

def quick_restart():
    global translator_active
    was_active = translator_active
    if was_active:
        translator_active = False
        time.sleep(0.1)  # Small delay to ensure clean deactivation
        translator_active = True
        threading.Thread(target=monitor_clipboard, args=(current_dictionary, current_dictionary_type), daemon=True).start()

def set_palette(name):
    import time
    global current_palette
    current_palette = color_palettes[name]
    save_palette(name)
    exe_path = sys.argv[0]
    # Create a temporary batch file to restart the app
    bat_content = f"""
    @echo off
    timeout /t 2 >nul
    start "" "{exe_path}"
    """
    with tempfile.NamedTemporaryFile('w', suffix='.bat', delete=False) as bat_file:
        bat_file.write(bat_content)
        bat_path = bat_file.name
    os.startfile(bat_path)
    os._exit(0)

def load_dictionary(json_file, dictionary_type):
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if dictionary_type == "translations":
                return {preprocess_text(key): value for key, value in data.items()}
            else:  # definitions dictionary
                return {preprocess_text(item["term"]): item["definition"] for item in data["definitions"]}
    except Exception as e:
        print(f"Error loading dictionary: {e}")
        return {}

def preprocess_text(text):
    return re.sub(r'[^\w\s]', '', text.lower()).strip()

def is_english(text):
    # More permissive regex to allow longer text for definitions
    return bool(re.match(r'^[a-zA-Z0-9\s.,!?;:\'"()-]+$', text))

def is_valid_input(text, dictionary_type):
    if dictionary_type == "translations":
        return len(text) <= 15 and is_english(text)
    else:  # definitions
        # Allow longer text for definitions, but still check for English
        return len(text) <= 50 and is_english(text) and not any(ext in text.lower() for ext in ['.com', '.org', '.net', '.jpg', '.png', '.gif', 'http', 'www'])

def translate_text(eng_text, dictionary, dictionary_type):
    processed_text = preprocess_text(eng_text)
    
    if dictionary_type == "definitions":
        # For definitions dictionary, implement smarter search
        best_match = None
        best_score = 0
        
        # First try exact match
        if processed_text in dictionary:
            return dictionary[processed_text]
            
        # Then try partial matches with scoring
        for term in dictionary.keys():
            # Check if the search term is part of a larger term
            if processed_text in term:
                # Calculate a score based on:
                # 1. Length of the match (longer matches are better)
                # 2. Position of the match (matches at the end are better)
                # 3. Whether it's a complete word match
                score = 0
                
                # Length score (longer matches get higher score)
                score += len(processed_text) / len(term) * 0.4
                
                # Position score (end matches get higher score)
                if term.endswith(processed_text):
                    score += 0.4
                elif term.startswith(processed_text):
                    score += 0.2
                    
                # Complete word match score
                if ' ' + processed_text + ' ' in ' ' + term + ' ':
                    score += 0.2
                    
                if score > best_score:
                    best_score = score
                    best_match = term
        
        # Only return a match if the score is high enough
        if best_score > 0.4 and best_match:
            return f"{best_match}: {dictionary[best_match]}"
            
        # If no good match found, try fuzzy matching as fallback
        closest_matches = get_close_matches(processed_text, dictionary.keys(), n=1, cutoff=0.6)
        if closest_matches:
            return f"{closest_matches[0]}: {dictionary[closest_matches[0]]}"
            
    else:  # For translations dictionary, keep existing behavior
        if processed_text in dictionary:
            return dictionary[processed_text]
        else:
            closest_matches = get_close_matches(processed_text, dictionary.keys(), n=1, cutoff=0.6)
            if closest_matches:
                return f"{closest_matches[0]}: {dictionary[closest_matches[0]]}"
    
    return "Translation not found."

def show_translation(original, translation, dictionary_type):
    global current_translation
    current_translation = translation

    def fade_in(window, alpha=0):
        if alpha < 1:
            alpha += 0.05
            window.attributes("-alpha", alpha)
            window.after(30, lambda: fade_in(window, alpha))

    def fade_out():
        alpha = root.attributes("-alpha")
        if alpha > 0:
            root.attributes("-alpha", alpha - 0.05)
            root.after(30, fade_out)
        else:
            root.destroy()

    def close_window():
        keyboard.unhook(hook_id)
        fade_out()

    def on_key_event(event):
        if event.event_type == keyboard.KEY_DOWN and event.name in ['ctrl', 'ctrl_l', 'ctrl_r']:
            root.after(0, close_window)

    root = Tk()
    # Adjust window size based on dictionary type
    if dictionary_type == "translations":
        root.geometry(f"500x250+{root.winfo_screenwidth() - 520}+30")
    else:
        root.geometry(f"600x400+{root.winfo_screenwidth() - 620}+30")  # Larger window for definitions
    
    root.configure(bg=current_palette["bg"])
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0)
    root.overrideredirect(True)

    fade_in(root)

    # Border frame with colored border and solid relief
    border_frame = Frame(root, bg=current_palette["border"], bd=4, relief="solid")
    border_frame.pack(fill="both", expand=True, padx=2, pady=2)

    # Content frame directly inside border_frame (no scrollbar/canvas)
    content_frame = Frame(border_frame, bg=current_palette["bg"])
    content_frame.pack(fill="both", expand=True, padx=padding, pady=padding)

    # Adjust labels based on dictionary type
    if dictionary_type == "translations":
        original_label = Label(content_frame, text="Original:", font=("Bahnschrift", 18, "bold"), 
                             fg=current_palette["text_fg"], bg=current_palette["bg"])
        translated_label = Label(content_frame, text="Translated:", font=("Bahnschrift", 18, "bold"), 
                               fg=current_palette["translation_fg"], bg=current_palette["bg"])
    else:
        original_label = Label(content_frame, text="Term:", font=("Bahnschrift", 18, "bold"), 
                             fg=current_palette["text_fg"], bg=current_palette["bg"])
        translated_label = Label(content_frame, text="Definition:", font=("Bahnschrift", 18, "bold"), 
                               fg=current_palette["translation_fg"], bg=current_palette["bg"])

    original_text_label = Label(content_frame, text=original, font=("Bahnschrift", 18), 
                              fg=current_palette["text_fg"], bg=current_palette["bg"], wraplength=460, anchor="center", justify="center")

    # RTL fix: If translation contains Arabic, prepend RTL mark
    def is_arabic(text):
        return any('\u0600' <= c <= '\u06FF' or '\u0750' <= c <= '\u077F' or '\u08A0' <= c <= '\u08FF' for c in text)

    translation_display = translation
    if is_arabic(translation):
        translation_display = '\u200F' + translation

    # Use Text widget for better RTL support
    translated_text_widget = Text(content_frame, font=("Bahnschrift", 16),
                                  fg=current_palette["translated_text_fg"], bg=current_palette["bg"],
                                  wrap="word", height=2, width=30, borderwidth=0, highlightthickness=0)
    translated_text_widget.tag_configure("center", justify='center')
    translated_text_widget.insert("1.0", translation_display, "center")
    translated_text_widget.config(state=DISABLED)

    original_label.pack(pady=(10, 0))
    original_text_label.pack(pady=2, fill="x")
    translated_label.pack(pady=(10, 0))
    translated_text_widget.pack(pady=5, fill="x", expand=True)

    hook_id = keyboard.hook(on_key_event)
    
    # Only auto-close for translations, keep definitions window open until Ctrl is pressed
    if dictionary_type == "translations":
        root.after(8000, close_window)
    
    root.mainloop()

def show_status_message(message, duration=500):  # Default duration is 500ms
    def fade_out():
        alpha = root.attributes("-alpha")
        if alpha > 0:
            root.attributes("-alpha", alpha - 0.05)
            root.after(30, fade_out)
        else:
            root.destroy()

    root = Tk()
    root.geometry("300x100+{}+{}".format(
        int(root.winfo_screenwidth()/2 - 150),
        int(root.winfo_screenheight()/2 - 50)
    ))
    root.configure(bg=current_palette["bg"])
    root.attributes("-topmost", True)
    root.attributes("-alpha", 1)
    root.overrideredirect(True)

    Label(root, text=message, font=("Bahnschrift", 18), fg=current_palette["border"], bg=current_palette["bg"]).pack(expand=True)

    root.after(duration, fade_out)  # Use the provided duration
    root.mainloop()

def monitor_clipboard(dictionary, dictionary_type):
    global translator_active
    last_text = ""
    while translator_active:
        try:
            current_text = pyperclip.paste()
            if (current_text != last_text and is_valid_input(current_text, dictionary_type)):
                translation = translate_text(current_text, dictionary, dictionary_type)
                show_translation(current_text, translation, dictionary_type)
                last_text = current_text
            time.sleep(0.1)
        except Exception as e:
            print(f"Error: {e}")

def copy_translation_to_clipboard():
    global current_translation
    if current_translation and current_translation != "Translation not found.":
        pyperclip.copy(current_translation)
        show_status_message("Copied to Clipboard! ✅", 500)

def toggle_translator(action):
    global translator_active
    if action == "activate" and not translator_active:
        translator_active = True
        threading.Thread(target=monitor_clipboard, args=(current_dictionary, current_dictionary_type), daemon=True).start()
        show_status_message("Translator Activated! 🚀", 500)
    elif action == "deactivate" and translator_active:
        translator_active = False
        show_status_message("Translator Deactivated! ❌", 500)

def set_dictionary_type(dict_type):
    global current_dictionary_type, current_dictionary
    current_dictionary_type = dict_type
    if dict_type == "translations":
        current_dictionary = translations_dictionary
    else:
        current_dictionary = definitions_dictionary
    save_dictionary_type(dict_type)
    quick_restart()

def save_dictionary_type(dict_type):
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    config["dictionary_type"] = dict_type
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f)

def load_saved_dictionary_type():
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("dictionary_type", "translations")
        except:
            pass
    return "translations"

def show_floating_tab():
    floating = Tk()
    floating.geometry("5x50+0+100")
    floating.configure(bg=current_palette["border"])
    floating.overrideredirect(True)
    floating.attributes("-topmost", True)
    floating.attributes("-alpha", 1)

    icon_img = Image.open(resource_path("settings_icon.png")).resize((20, 20), Image.Resampling.LANCZOS)
    icon = ImageTk.PhotoImage(icon_img)

    width = 5
    target_width = 50

    floating.bind("<Enter>", lambda e: floating.config(cursor="hand2"))
    floating.bind("<Leave>", lambda e: floating.config(cursor=""))

    def animate_expand(current_width):
        if current_width < target_width:
            new_width = current_width + 5
            floating.geometry(f"{new_width}x50+0+100")
            floating.after(10, lambda: animate_expand(new_width))

    def animate_collapse(current_width):
        if current_width > 5:
            new_width = current_width - 5
            floating.geometry(f"{new_width}x50+0+100")
            floating.after(10, lambda: animate_collapse(new_width))

    def expand(event=None):
        animate_expand(width)
        settings_button.place(x=10, y=10)

    def collapse(event=None):
        animate_collapse(target_width)
        settings_button.place_forget()

    def open_settings():
        global settings_window
        settings_window = Toplevel()
        settings_window.geometry("420x600+100+200")  # Increased height for new buttons
        settings_window.title("Settings")
        settings_window.configure(bg=current_palette["bg"])
        settings_window.attributes("-topmost", True)

        Label(settings_window, text="🔧 Translator Hotkeys", bg=current_palette["bg"], 
              fg=current_palette["translation_fg"], font=("Bahnschrift", 16, "bold")).pack(pady=(10, 5))

        Label(
            settings_window,
            text="• Press Ctrl + Shift + 1 to activate\n"
                 "• Press Ctrl + Shift + 2 to deactivate\n"
                 "• Press Ctrl + Shift + 3 to switch dictionaries\n"
                 "• Press Ctrl + Alt + C to copy translation\n"
                 "• Press Ctrl to close definition window",
            bg=current_palette["bg"], fg=current_palette["text_fg"], font=("Bahnschrift", 14), justify="left"
        ).pack(pady=5)

        # Dictionary Type Selection
        Label(settings_window, text="📚 Dictionary Type:", bg=current_palette["bg"], fg=current_palette["text_fg"], 
              font=("Bahnschrift", 13)).pack(pady=(20, 5))
        
        dict_type_var = StringVar(value=current_dictionary_type)
        
        def on_dict_type_change():
            set_dictionary_type(dict_type_var.get())
        
        Radiobutton(settings_window, text="Translations (Auto-close)", variable=dict_type_var, 
                    value="translations", command=on_dict_type_change, bg=current_palette["bg"], 
                    fg=current_palette["text_fg"], selectcolor=current_palette["bg"], activebackground=current_palette["bg"],
                    activeforeground=current_palette["text_fg"]).pack()
        
        Radiobutton(settings_window, text="Definitions (Ctrl to close)", variable=dict_type_var, 
                    value="definitions", command=on_dict_type_change, bg=current_palette["bg"], 
                    fg=current_palette["text_fg"], selectcolor=current_palette["bg"], activebackground=current_palette["bg"],
                    activeforeground=current_palette["text_fg"]).pack()

        Button(
            settings_window, text="Activate Translator", font=("Bahnschrift", 12, "bold"),
            bg=current_palette["button_bg"], fg=current_palette["button_fg"],
            activebackground=current_palette["button_active_bg"], activeforeground=current_palette["button_active_fg"],
            command=lambda: toggle_translator("activate")
        ).pack(pady=(20, 5))

        Button(
            settings_window, text="Deactivate Translator", font=("Bahnschrift", 12, "bold"),
            bg=current_palette["text_fg"], fg=current_palette["bg"],
            activebackground=current_palette["translation_fg"], activeforeground=current_palette["bg"],
            command=lambda: toggle_translator("deactivate")
        ).pack(pady=5)

        Label(settings_window, text="🎨 Choose a Palette:", bg=current_palette["bg"], fg=current_palette["text_fg"], 
              font=("Bahnschrift", 13)).pack(pady=(20, 5))

        for name in color_palettes:
            Button(
                settings_window, text=name, font=("Bahnschrift", 10),
                bg=color_palettes[name]["border"], fg=color_palettes[name]["bg"],
                command=lambda n=name: set_palette(n),
                relief="ridge", borderwidth=2, width=20
            ).pack(pady=2)

        # Add About Me button
        Button(
            settings_window, text="About Me", font=("Bahnschrift", 12, "bold"),
            bg=current_palette["button_bg"], fg=current_palette["button_fg"],
            activebackground=current_palette["button_active_bg"], activeforeground=current_palette["button_active_fg"],
            command=lambda: [settings_window.destroy(), show_about_window()]
        ).pack(pady=(20, 5))

        # Add Close Application button
        Button(
            settings_window, text="Close Application", font=("Bahnschrift", 12, "bold"),
            bg="#FF4444", fg="white",
            activebackground="#FF6666", activeforeground="white",
            command=lambda: [keyboard.unhook_all(), settings_window.destroy(), os._exit(0)]
        ).pack(pady=5)

        settings_window.mainloop()

    settings_button = Button(floating, image=icon, bg=current_palette["border"], bd=0,
                             activebackground=current_palette["border"], command=open_settings, relief="flat", highlightthickness=5)
    settings_button.image = icon
    settings_button.place_forget()

    floating.bind("<Enter>", expand)
    floating.bind("<Leave>", collapse)
    floating.mainloop()

# Start floating tab
threading.Thread(target=show_floating_tab, daemon=True).start()

# Load dictionaries
script_dir = os.path.dirname(os.path.abspath(__file__))
translations_file_path = resource_path("dictionary1.json")
definitions_file_path = resource_path("dictionary2.json")

translations_dictionary = load_dictionary(translations_file_path, "translations")
definitions_dictionary = load_dictionary(definitions_file_path, "definitions")

# Set initial dictionary based on saved preference
current_dictionary_type = load_saved_dictionary_type()
current_dictionary = translations_dictionary if current_dictionary_type == "translations" else definitions_dictionary

# Print dictionary sizes for debugging
print(f"Translations dictionary size: {len(translations_dictionary)}")
print(f"Definitions dictionary size: {len(definitions_dictionary)}")

# Add new function for dictionary switching
def toggle_dictionary():
    global current_dictionary_type
    if current_dictionary_type == "translations":
        set_dictionary_type("definitions")
    else:
        set_dictionary_type("translations")
    show_status_message(f"{current_dictionary_type} dictionary!🔄", 1000)  # 1 second for dictionary switching

# Add keyboard shortcuts for dictionary switching
keyboard.add_hotkey("ctrl+shift+3", toggle_dictionary)

keyboard.add_hotkey(activate_key, lambda: toggle_translator("activate"))
keyboard.add_hotkey(deactivate_key, lambda: toggle_translator("deactivate"))
keyboard.add_hotkey(copy_key, copy_translation_to_clipboard)

print("Press Ctrl + Shift + 1 to activate and Ctrl + Shift + 2 to deactivate.")
print("Press Ctrl + Alt + C to copy the translation to the clipboard.")
print("Press Ctrl + Shift + 3 to switch between dictionaries.")

def show_about_window():
    about_window = Toplevel()
    about_window.geometry("400x300+150+200")
    about_window.title("About")
    about_window.configure(bg=current_palette["bg"])
    about_window.attributes("-topmost", True)
    
    # Add content to about window
    Label(about_window, text="About Me", font=("Bahnschrift", 20, "bold"),
          bg=current_palette["bg"], fg=current_palette["translation_fg"]).pack(pady=(20, 10))
    
    Label(about_window, text="Made by Raafat Reda", font=("Bahnschrift", 14),
          bg=current_palette["bg"], fg=current_palette["text_fg"]).pack(pady=5)
    
    Label(about_window, text="Phone: 01022779263", font=("Bahnschrift", 14),
          bg=current_palette["bg"], fg=current_palette["text_fg"]).pack(pady=5)
    
    Label(about_window, text="Email: rafat2782005@gmail.com", font=("Bahnschrift", 14),
          bg=current_palette["bg"], fg=current_palette["text_fg"]).pack(pady=5)
    
    Button(about_window, text="Close", font=("Bahnschrift", 12),
           bg=current_palette["button_bg"], fg=current_palette["button_fg"],
           activebackground=current_palette["button_active_bg"],
           activeforeground=current_palette["button_active_fg"],
           command=about_window.destroy).pack(pady=20)

keyboard.wait()
