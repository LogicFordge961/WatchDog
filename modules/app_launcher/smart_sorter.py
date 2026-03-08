import os
import json
from typing import List, Dict
import psutil

class SmartAppSorter:
    def __init__(self):
        self.categories = {
            'essential': ['notepad', 'calculator', 'settings', 'taskmgr', 'cmd', 'powershell'],
            'productivity': ['word', 'excel', 'powerpoint', 'onenote', 'outlook', 'thunderbird'],
            'browsers': ['chrome', 'firefox', 'edge', 'safari', 'opera', 'brave'],
            'media': ['vlc', 'spotify', 'itunes', 'media player', 'vlc', 'audacity'],
            'development': ['vscode', 'visual studio', 'pycharm', 'sublime', 'notepad++', 'git'],
            'gaming': ['steam', 'epic', 'origin', 'uplay', 'battle.net', 'minecraft'],
            'communication': ['discord', 'teams', 'skype', 'zoom', 'slack', 'telegram'],
            'graphics': ['photoshop', 'gimp', 'paint', 'illustrator', 'blender'],
            'utilities': ['7zip', 'winrar', 'ccleaner', 'malwarebytes', 'defrag']
        }
    
    def categorize_app(self, app_name: str) -> str:
        """Use AI-like logic to categorize applications"""
        app_lower = app_name.lower()
        
        # Check each category
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in app_lower:
                    return category
        
        # Fallback categorization based on common patterns
        if any(word in app_lower for word in ['game', 'play', 'steam']):
            return 'gaming'
        elif any(word in app_lower for word in ['edit', 'develop', 'code', 'studio']):
            return 'development'
        elif any(word in app_lower for word in ['browser', 'chrome', 'firefox', 'edge']):
            return 'browsers'
        elif any(word in app_lower for word in ['music', 'video', 'media', 'player']):
            return 'media'
        elif any(word in app_lower for word in ['mail', 'email', 'outlook', 'thunderbird']):
            return 'communication'
        else:
            return 'other'
    
    def filter_real_apps(self, apps: List[Dict]) -> List[Dict]:
        """Filter out junk/unwanted applications using smart criteria"""
        filtered_apps = []
        
        # Common junk/exclude patterns
        exclude_patterns = [
            'unins', 'uninstall', 'helper', 'service', 'background',
            'updater', 'update', 'crash', 'report', 'log', 'temp',
            'cache', 'setup', 'installer', 'patch', 'support'
        ]
        
        # Common legitimate app patterns
        include_patterns = [
            'notepad', 'chrome', 'firefox', 'edge', 'steam', 'discord',
            'office', 'word', 'excel', 'powerpoint', 'vscode', 'sublime',
            'photoshop', 'vlc', 'spotify', 'calculator', 'settings'
        ]
        
        for app in apps:
            app_name = app.get('name', '').lower()
            app_path = app.get('path', '').lower()
            
            # Skip obviously junk apps
            if any(pattern in app_name for pattern in exclude_patterns):
                continue
                
            # Skip apps in system directories that aren't user apps
            if any(dir_name in app_path for dir_name in ['system32', 'syswow64', 'windows']):
                # But allow some exceptions
                if not any(include_word in app_name for include_word in include_patterns):
                    continue
            
            # Skip very small executables (likely helpers)
            if app.get('size', 0) < 1024 * 100:  # Less than 100KB
                # But allow some exceptions
                if not any(include_word in app_name for include_word in include_patterns):
                    continue
            
            # Add to filtered list
            filtered_apps.append(app)
        
        return filtered_apps
    
    def rank_apps_by_importance(self, apps: List[Dict]) -> List[Dict]:
        """Rank applications by importance/usefulness"""
        # Get currently running processes for reference
        running_processes = []
        try:
            for proc in psutil.process_iter(['name']):
                running_processes.append(proc.info['name'].lower().replace('.exe', ''))
        except Exception as e:
            pass
        
        ranked_apps = []
        for app in apps:
            app_name = app.get('name', '').lower()
            score = 0
            
            # Boost score for commonly used apps
            common_apps = ['chrome', 'firefox', 'notepad', 'vscode', 'steam', 'discord', 
                          'spotify', 'word', 'excel', 'powerpoint', 'outlook']
            if any(common_app in app_name for common_app in common_apps):
                score += 10
            
            # Boost score for recently used apps (check if running)
            if app_name.replace('.exe', '') in running_processes:
                score += 5
            
            # Boost score for larger, more substantial apps
            if app.get('size', 0) > 1024 * 1024 * 50:  # 50MB+
                score += 3
            
            # Add score to app
            app['importance_score'] = score
            ranked_apps.append(app)
        
        # Sort by importance score (descending)
        return sorted(ranked_apps, key=lambda x: x.get('importance_score', 0), reverse=True)
    
    def get_top_apps(self, apps: List[Dict], count: int = 20) -> List[Dict]:
        """Get the most important/frequently used apps"""
        filtered = self.filter_real_apps(apps)
        ranked = self.rank_apps_by_importance(filtered)
        return ranked[:count]
    
    def group_apps_by_category(self, apps: List[Dict]) -> Dict[str, List[Dict]]:
        """Group apps into categories"""
        categorized = {}
        for app in apps:
            category = self.categorize_app(app.get('name', ''))
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(app)
        return categorized

# Global instance
smart_sorter = SmartAppSorter()
