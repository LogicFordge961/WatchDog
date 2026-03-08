import sys
from modules.app_launcher.scanner import AppScanner
from modules.app_launcher.launcher import AppLauncher
from modules.process_manager.monitor import ProcessMonitor
from ai.assistant import AIPoweredAssistant
from utils.updater import updater  # Import updater

class CommandParser:
    def __init__(self):
        self.ai_assistant = AIPoweredAssistant()
        self.app_scanner = AppScanner()
        self.app_launcher = AppLauncher()
        self.process_monitor = ProcessMonitor()
        self.should_exit = False
    
    def handle_command(self, command_line):
        parts = command_line.strip().split(' ', 1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # Direct command handlers
        direct_handlers = {
            'scan': self.handle_scan_apps,
            'monitor': self.handle_monitor_processes,
            'exit': self.handle_exit,
            'quit': self.handle_exit,
            'bye': self.handle_exit,
            'launch': self.handle_launch,
            'open': self.handle_launch,
            'kill': self.handle_kill,
            'update': self.handle_update,  # Add update handler
            'upgrade': self.handle_update  # Add upgrade handler
        }
        
        # Check for direct commands first
        if command in direct_handlers:
            direct_handlers[command](args)
            return self.should_exit
        
        # Everything else goes to AI (natural language processing)
        else:
            self.handle_natural_language(command_line)
            return self.should_exit
    
    def handle_natural_language(self, natural_command):
        """Handle natural language input with AI"""
        if self.ai_assistant:
            print("🤖 Let me help you with that...")
            response = self.ai_assistant.query_ai(natural_command)
            print(f"💡 {response['response']}")
        else:
            print("❌ AI module not available. Try specific commands like 'launch', 'kill', 'scan', etc.")
    
    def handle_exit(self, args):
        """Handle exit commands"""
        print("👋 Goodbye!")
        self.should_exit = True
    
    def handle_scan_apps(self, args):
        print("🔍 Scanning for applications...")
        try:
            apps = self.app_scanner.scan_executables()
            print(f"Found {len(apps)} applications")
            
            # Rebuild registry
            registry = {}
            for app in apps:
                name_lower = app['name'].lower()
                if name_lower not in registry:
                    registry[name_lower] = app
            
            self.app_launcher.save_registry(registry)
            print("✅ Application registry updated")
            
            # Show sample of found apps
            app_names = list(registry.keys())[:10]
            for name in app_names:
                print(f"  - {name}")
            if len(registry) > 10:
                print(f"  ... and {len(registry) - 10} more")
        except Exception as e:
            print(f"❌ Error scanning apps: {e}")
    
    def handle_launch(self, args):
        if args:
            try:
                result = self.app_launcher.launch_application(args)
                print(result)
            except Exception as e:
                print(f"❌ Error launching application: {e}")
        else:
            print("Usage: launch <application_name>")
    
    def handle_kill(self, args):
        if args:
            try:
                killed = self.process_monitor.kill_process_by_name(args)
                if killed:
                    print(f"✅ Killed {len(killed)} process(es)")
                    for proc in killed:
                        print(f"  - {proc['name']} (PID: {proc['pid']})")
                else:
                    print(f"❌ No processes found matching '{args}'")
            except Exception as e:
                print(f"❌ Error killing process: {e}")
        else:
            print("Usage: kill <process_name_or_pid>")
    
    def handle_monitor_processes(self, args):
        print("📊 Monitoring system processes...")
        try:
            processes = self.process_monitor.get_running_processes()
            print(f"Running {len(processes)} processes")
            
            # Filter out empty processes
            valid_processes = [p for p in processes if p and p.get('name')]
            
            # Show top 10 CPU using processes
            sorted_processes = sorted(valid_processes, key=lambda x: x.get('cpu_percent', 0) or 0, reverse=True)
            print("\nTop CPU consumers:")
            for proc in sorted_processes[:10]:
                if proc and proc.get('name'):
                    cpu = proc.get('cpu_percent', 0) or 0
                    mem = proc.get('memory_percent', 0) or 0
                    print(f"  {proc['name']} (PID: {proc['pid']}) - CPU: {cpu:.1f}% Mem: {mem:.1f}%")
        except Exception as e:
            print(f"❌ Error monitoring processes: {e}")
    
    def handle_update(self, args):
        """Handle update command"""
        print("🔄 Checking for updates...")
        try:
            if updater.perform_update():
                print("✅ Update completed successfully!")
                # The updater will restart the app, so we don't need to do anything here
            else:
                print("ℹ️  No updates available or update cancelled")
        except Exception as e:
            print(f"❌ Update failed: {e}")
