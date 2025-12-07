"""
Hotkey Manager for MedTranslate Pro
Handles global keyboard shortcuts
"""

import keyboard
from typing import Dict, Callable, Optional


class HotkeyManager:
    """Manages global hotkeys"""
    
    def __init__(self, config: dict):
        """
        Initialize hotkey manager
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.hotkeys = config.get('hotkeys', {})
        self.registered_hotkeys = {}
        self.callbacks = {}
    
    def register_hotkey(self, name: str, callback: Callable):
        """
        Register a hotkey with callback
        
        Args:
            name: Hotkey name (from config)
            callback: Function to call when hotkey is pressed
        """
        if name not in self.hotkeys:
            print(f"Warning: Hotkey '{name}' not found in config")
            return
        
        hotkey_combination = self.hotkeys[name]
        
        try:
            # Unregister if already registered
            if name in self.registered_hotkeys:
                keyboard.remove_hotkey(self.registered_hotkeys[name])
            
            # Register new hotkey
            hook_id = keyboard.add_hotkey(hotkey_combination, callback, suppress=False)
            self.registered_hotkeys[name] = hook_id
            self.callbacks[name] = callback
            
            print(f"✅ Registered hotkey: {name} = {hotkey_combination}")
        
        except Exception as e:
            print(f"Error registering hotkey {name} ({hotkey_combination}): {e}")
    
    def unregister_hotkey(self, name: str):
        """Unregister a hotkey"""
        if name in self.registered_hotkeys:
            try:
                keyboard.remove_hotkey(self.registered_hotkeys[name])
                del self.registered_hotkeys[name]
                del self.callbacks[name]
                print(f"Unregistered hotkey: {name}")
            except Exception as e:
                print(f"Error unregistering hotkey {name}: {e}")
    
    def unregister_all(self):
        """Unregister all hotkeys"""
        for name in list(self.registered_hotkeys.keys()):
            self.unregister_hotkey(name)
    
    def update_hotkey(self, name: str, new_combination: str):
        """
        Update hotkey combination
        
        Args:
            name: Hotkey name
            new_combination: New key combination (e.g., 'ctrl+shift+1')
        """
        # Update in config
        self.hotkeys[name] = new_combination
        
        # Re-register if it was registered
        if name in self.callbacks:
            callback = self.callbacks[name]
            self.register_hotkey(name, callback)
    
    def get_hotkey(self, name: str) -> Optional[str]:
        """Get hotkey combination by name"""
        return self.hotkeys.get(name)
    
    def is_registered(self, name: str) -> bool:
        """Check if hotkey is registered"""
        return name in self.registered_hotkeys
    
    def check_conflicts(self) -> Dict[str, list]:
        """
        Check for hotkey conflicts
        
        Returns:
            Dictionary of conflicting hotkeys
        """
        conflicts = {}
        seen = {}
        
        for name, combination in self.hotkeys.items():
            if combination in seen:
                if combination not in conflicts:
                    conflicts[combination] = [seen[combination]]
                conflicts[combination].append(name)
            else:
                seen[combination] = name
        
        return conflicts


# Example usage
if __name__ == "__main__":
    config = {
        "hotkeys": {
            "start_translator": "ctrl+shift+1",
            "stop_translator": "ctrl+shift+2",
            "copy_result": "ctrl+alt+c"
        }
    }
    
    manager = HotkeyManager(config)
    
    # Register hotkeys
    manager.register_hotkey("start_translator", lambda: print("Start!"))
    manager.register_hotkey("stop_translator", lambda: print("Stop!"))
    
    # Check conflicts
    conflicts = manager.check_conflicts()
    if conflicts:
        print(f"⚠️ Conflicts found: {conflicts}")
    else:
        print("✅ No conflicts")
    
    # Keep running to test hotkeys
    print("Press Ctrl+C to exit")
    keyboard.wait()
