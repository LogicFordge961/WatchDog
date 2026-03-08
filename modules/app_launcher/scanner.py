import os
import psutil
from .smart_sorter import smart_sorter

class AppScanner:
    def __init__(self):
        self.scan_paths = [
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            os.path.expanduser("~\\AppData\\Local")
        ]
    
    def scan_executables(self):
        """Scan for executable files with smart filtering"""
        apps = []
        scanned_paths = set()  # Avoid duplicate scans
        
        for path in self.scan_paths:
            if os.path.exists(path):
                try:
                    # Walk through directory tree
                    for root, dirs, files in os.walk(path):
                        # Skip system directories
                        if any(skip_dir in root.lower() for skip_dir in ['system32', 'syswow64', 'windows\\servicing']):
                            continue
                        
                        # Limit depth to avoid excessive scanning
                        path_parts = root.replace(path, '').count(os.sep)
                        if path_parts > 4:  # Don't go too deep
                            continue
                        
                        for file in files:
                            if file.endswith('.exe') and not file.startswith('unins'):
                                full_path = os.path.join(root, file)
                                
                                # Avoid duplicate paths
                                if full_path.lower() in scanned_paths:
                                    continue
                                scanned_paths.add(full_path.lower())
                                
                                try:
                                    # Get file size
                                    size = os.path.getsize(full_path) if os.path.exists(full_path) else 0
                                    
                                    # Skip very small files unless they're known apps
                                    if size < 1024 * 100:  # Less than 100KB
                                        known_small_apps = ['notepad.exe', 'calc.exe', 'mspaint.exe']
                                        if file.lower() not in known_small_apps:
                                            continue
                                    
                                    apps.append({
                                        'name': file.replace('.exe', ''),
                                        'path': full_path,
                                        'size': size
                                    })
                                except (PermissionError, OSError):
                                    continue  # Skip files we can't access
                except PermissionError:
                    continue  # Skip directories we can't access
        
        # Apply smart filtering and sorting
        filtered_apps = smart_sorter.filter_real_apps(apps)
        ranked_apps = smart_sorter.rank_apps_by_importance(filtered_apps)
        
        return ranked_apps
    
    def get_categorized_apps(self):
        """Get apps grouped by category"""
        apps = self.scan_executables()
        return smart_sorter.group_apps_by_category(apps)
    
    def get_top_apps(self, count=20):
        """Get the most important apps"""
        apps = self.scan_executables()
        return smart_sorter.get_top_apps(apps, count)
