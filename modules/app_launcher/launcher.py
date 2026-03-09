# modules/app_launcher/launcher.py
import os
import subprocess
import json
import platform
from core.logger import get_logger
from modules.process_manager.monitor import ProcessMonitor

class AppLauncher:
    def __init__(self, registry_file="data/registry.json"):
        self.registry_file = registry_file
        self.logger = get_logger("AppLauncher")
        self.registry = self.load_registry()
        self.os_type = platform.system().lower()
    
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
    
    def get_default_app_path(self, app_name):
        """Get default application path based on OS"""
        app_name_lower = app_name.lower()
        
        if self.os_type == "windows":
            # Windows common paths
            windows_apps = {
                'chrome': 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
                'firefox': 'C:\\Program Files\\Mozilla Firefox\\firefox.exe',
                'notepad': 'notepad.exe',
                'calculator': 'calc.exe',
                'cmd': 'cmd.exe',
                'powershell': 'powershell.exe'
            }
            return windows_apps.get(app_name_lower)
            
        elif self.os_type == "darwin":  # macOS
            mac_apps = {
                'chrome': '/Applications/Google Chrome.app',
                'firefox': '/Applications/Firefox.app',
                'safari': '/Applications/Safari.app',
                'calculator': 'Calculator'
            }
            return mac_apps.get(app_name_lower)
            
        else:  # Linux
            linux_commands = {
                'chrome': 'google-chrome',
                'firefox': 'firefox',
                'notepad': 'gedit',
                'calculator': 'gnome-calculator',
                'terminal': 'gnome-terminal'
            }
            return linux_commands.get(app_name_lower)
    
    def launch_application(self, app_name):
        """Launch application by name"""
        try:
            # First try to find in registry
            app = self.find_application(app_name)
            
            if app and os.path.exists(app.get('path', '')):
                try:
                    if self.os_type == "windows":
                        subprocess.Popen([app['path']], shell=True)
                    elif self.os_type == "darwin":  # macOS
                        subprocess.Popen(['open', app['path']])
                    else:  # Linux
                        subprocess.Popen([app['path']])
                    
                    self.logger.info(f"Launched {app['name']} from {app['path']}")
                    return f"✅ Launched {app['name']}"
                except Exception as e:
                    self.logger.error(f"Failed to launch {app['name']}: {e}")
                    return f"❌ Failed to launch {app['name']}: {e}"
            
            else:
                # Try default paths or commands
                default_path = self.get_default_app_path(app_name)
                if default_path:
                    try:
                        if self.os_type == "windows":
                            subprocess.Popen(default_path, shell=True)
                        elif self.os_type == "darwin":  # macOS
                            subprocess.Popen(['open', '-a', default_path])
                        else:  # Linux
                            subprocess.Popen(default_path.split())
                        
                        self.logger.info(f"Launched {app_name} using default path: {default_path}")
                        return f"✅ Launched {app_name}"
                    except Exception as e:
                        self.logger.error(f"Failed to launch {app_name} with default path: {e}")
                        return f"❌ Failed to launch {app_name}: {e}"
                else:
                    # Try to find running process instead
                    monitor = ProcessMonitor()
                    processes = monitor.find_process_by_name(app_name)
                    if processes:
                        return f"✅ {app_name} is already running (PID: {processes[0]['pid']})"
                    else:
                        return f"❌ Application '{app_name}' not found. Try 'scan' to refresh the registry or install the application."
                        
        except Exception as e:
            self.logger.error(f"Error in launch_application: {e}")
            return f"❌ Error launching application: {e}"
