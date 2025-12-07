from utils.config_manager import ConfigManager

print("Applying Emergency Fix...")
cm = ConfigManager()

# Switch to 'libre' (Bing/Google wrapper) as it is free and unlimited
current = cm.config['translation']['active_source']
print(f"Current source: {current}")

cm.config['translation']['active_source'] = 'libre'
print("Switched default source to: libre (Google/Bing)")

cm.save_config()
print("Fixed! Please restart the application.")
