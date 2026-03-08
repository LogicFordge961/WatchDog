#!/usr/bin/env python3
"""
WatchDog - System Intelligence Framework
"""

import sys
import os
import json
import argparse

# Add this at the VERY TOP to fix path issues
# When frozen by PyInstaller, use sys._MEIPASS (temporary folder where bundle is unpacked).
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
else:
    # Running as script
    application_path = os.path.dirname(os.path.abspath(__file__))

# Add application path to Python path
sys.path.insert(0, application_path)

# Change current working directory to application directory
os.chdir(application_path)

# Rest of your imports (they should work now)
try:
    from core.cli import WatchDogCLI
    from core.logger import setup_logging
    from utils.updater import check_for_updates
except ImportError as e:
    print(f"❌ Import error: {e}")
    input("Press Enter to exit...")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="WatchDog - System Intelligence Framework")
    parser.add_argument('--cli', action='store_true', help='Launch CLI interface')
    args = parser.parse_args()

    try:
        # Setup logging
        setup_logging()

        # Load config for auto-update and version
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config', 'settings.json'))
        auto_update = False
        app_version = '1.0.0'
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                    auto_update = bool(cfg.get('auto_update', False))
                    app_version = cfg.get('version', app_version)
        except Exception:
            pass

        print(f"🚀 Starting WatchDog v{app_version}...")

        # Check for updates (honor config auto_update)
        check_for_updates(auto_update=auto_update)

        if args.cli:
            # Start CLI
            print(f"🤖 Welcome to WatchDog v{app_version}. Type 'help' for commands.")
            cli = WatchDogCLI()
            cli.run()
        else:
            # Launch GUI
            try:
                import tkinter as tk
                from ui.gui import WatchDogGUI
                root = tk.Tk()
                app = WatchDogGUI(root)
                root.mainloop()
            except ImportError:
                print("❌ Tkinter not available. Install tkinter or use --cli mode.")
                sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
