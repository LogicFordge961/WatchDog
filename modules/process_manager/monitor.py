# modules/process_manager/monitor.py
import psutil
import time
from core.logger import get_logger

class ProcessMonitor:
    def __init__(self):
        self.logger = get_logger("ProcessMonitor")
    
    def get_running_processes(self):
        """Get all running processes with proper error handling"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                proc_info = proc.info
                # Only include processes with valid names
                if proc_info and proc_info.get('name'):
                    processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Skip processes we can't access
                continue
            except Exception as e:
                # Log but don't crash on individual process errors
                self.logger.debug(f"Could not access process info: {e}")
                continue
        return processes
    
    def kill_process_by_name(self, name):
        """Kill process by name with better matching"""
        killed = []
        name_lower = name.lower()
        
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                proc_name = proc.info['name'].lower()
                proc_name_no_ext = proc_name.replace('.exe', '')
                
                # Match by exact name, partial name, or PID
                if (name_lower in proc_name or 
                    name_lower in proc_name_no_ext or
                    name_lower == str(proc.info['pid'])):
                    proc.kill()
                    killed.append({
                        'name': proc.info['name'],
                        'pid': proc.info['pid']
                    })
                    self.logger.info(f"Killed process: {proc.info['name']} (PID: {proc.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as e:
                self.logger.warning(f"Error killing process {proc.info.get('name', 'Unknown')}: {e}")
        
        return killed
    
    def find_process_by_name(self, name):
        """Find processes by name (used for detection)"""
        found = []
        name_lower = name.lower()
        
        for proc in psutil.process_iter(['name', 'pid', 'status']):
            try:
                proc_name = proc.info['name'].lower()
                proc_name_no_ext = proc_name.replace('.exe', '')
                
                # Flexible matching
                if (name_lower in proc_name or 
                    name_lower in proc_name_no_ext or
                    proc_name_no_ext in name_lower):
                    found.append({
                        'name': proc.info['name'],
                        'pid': proc.info['pid'],
                        'status': proc.info.get('status', 'unknown')
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return found
