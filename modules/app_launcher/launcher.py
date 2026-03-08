# modules/app_launcher/launcher.py
import os
import subprocess
import json
from core.logger import get_logger

class AppLauncher:
    def __init__(self, registry_file="data/registry.json"):
        self.registry_file = registry_file
        self.logger = get_logger("AppLauncher")
        self.registry = self.load_registry()
    
    def load_registry(self):
        """Load application registry from file"""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading registry: {e}")
                return {}
        return {}
    
    def save_registry(self, registry):
        """Save registry to file"""
        try:
            os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
            with open(self.registry_file, 'w') as f:
                json.dump(registry, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving registry: {e}")
    
    def find_application(self, app_name):
        """Find application by name with flexible matching"""
        app_name_lower = app_name.lower()
        
        # Direct match
        if app_name_lower in self.registry:
            return self.registry[app_name_lower]
        
        # Partial match
        for name, app in self.registry.items():
            if (app_name_lower in name or 
                name in app_name_lower or
                app_name_lower.replace(' ', '') in name.replace(' ', '')):
                return app
        
        # Special cases for common apps
        special_cases = {
            'discord': ['discord', 'discordapp'],
            'chrome': ['chrome', 'googlechrome', 'chromium'],
            'firefox': ['firefox', 'mozilla firefox'],
            'steam': ['steam', 'steamer'],
            'notepad': ['notepad', 'notepad++']
        }
        
        if app_name_lower in special_cases:
            for alt_name in special_cases[app_name_lower]:
                if alt_name in self.registry:
                    return self.registry[alt_name]
        
        return None
    
    def launch_application(self, app_name):
        """Launch application by name"""
        try:
            app = self.find_application(app_name)
            if app:
                try:
                    subprocess.Popen([app['path']], shell=True)
                    self.logger.info(f"Launched {app['name']} from {app['path']}")
                    return f"✅ Launched {app['name']}"
                except Exception as e:
                    self.logger.error(f"Failed to launch {app['name']}: {e}")
                    return f"❌ Failed to launch {app['name']}: {e}"
            else:
                # Try to find running process instead
                from modules.process_manager.monitor import ProcessMonitor
                monitor = ProcessMonitor()
                processes = monitor.find_process_by_name(app_name)
                if processes:
                    return f"✅ {app_name} is already running (PID: {processes[0]['pid']})"
                else:
                    return f"❌ Application '{app_name}' not found. Try 'scan' to refresh the registry."
        except Exception as e:
            self.logger.error(f"Error in launch_application: {e}")
            return f"❌ Error launching application: {e}"
