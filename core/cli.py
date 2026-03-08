import cmd
from core.command_parser import CommandParser

class WatchDogCLI(cmd.Cmd):
    intro = "🤖 Welcome to WatchDog v1.0. Type 'help' for commands."
    prompt = "watchdog> "
    
    def __init__(self):
        super().__init__()
        self.parser = CommandParser()
    
    def default(self, line):
        """Handle all commands through the parser"""
        should_exit = self.parser.handle_command(line)
        if should_exit:
            return True
    
    def do_help(self, arg):
        """Show help"""
        print("""
Available commands:
  run      - Run monitoring mode
  ai       - Ask AI assistant
  kill     - Kill processes
  scan     - Scan applications
  launch   - Launch applications
  open     - Open applications (same as launch)
  monitor  - Monitor system processes
  update   - Check for and install updates
  upgrade  - Same as update
  help     - Show this help
  exit     - Exit WatchDog
  quit     - Exit WatchDog
  bye      - Exit WatchDog
        """)
    
    def do_exit(self, arg):
        """Exit WatchDog"""
        return True
        
    def do_quit(self, arg):
        """Exit WatchDog"""
        return True
        
    def do_bye(self, arg):
        """Exit WatchDog"""
        return True
    
    def do_update(self, arg):
        """Check for and install updates"""
        self.parser.handle_command("update " + arg)
        return False  # Don't exit after update
    
    def do_upgrade(self, arg):
        """Check for and install updates (alias for update)"""
        self.parser.handle_command("update " + arg)
        return False  # Don't exit after update
    
    def run(self):
        """Run the CLI with proper error handling"""
        import sys
        import os
        
        # Check if we have an interactive terminal
        if not sys.stdin.isatty():
            print("❌ No interactive terminal available. WatchDog requires an interactive console to run.")
            print("💡 Try running: python watchdog.py")
            return
        
        try:
            self.cmdloop()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            return
        except Exception as e:
            print(f"\n❌ CLI Error: {e}")
            import traceback
            traceback.print_exc()
            return
