import json
import os
import sys

DEFAULT_SETTINGS = {
    "version": "1.0.0",
    "debug": False,
    "log_level": "INFO",
    "auto_update": True,
    "ai_enabled": True,
    "sync_enabled": False,
    "monitoring_interval": 5
}

class ConfigManager:
    def __init__(self, config_path="config/settings.json"):
        self.config_path = config_path
        self.settings = self.load_settings()
    
    def load_settings(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                return DEFAULT_SETTINGS.copy()
        else:
            self.save_settings(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS.copy()
    
    def save_settings(self, settings):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(settings, f, indent=2)
    
    def get(self, key, default=None):
        return self.settings.get(key, default)
    
    def set(self, key, value):
        self.settings[key] = value
        self.save_settings(self.settings)
    
    @staticmethod
    def get_config_path():
        if getattr(sys, 'frozen', False):
            return os.path.join(os.path.dirname(sys.executable), "config/settings.json")
        else:
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'settings.json')
