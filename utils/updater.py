import requests
import json
import os
import sys
import subprocess
import tempfile
import hashlib
import time
from packaging import version
from datetime import datetime
from core.logger import get_logger

logger = get_logger("Updater")

class GitHubUpdater:
    def __init__(self, repo_owner="yourusername", repo_name="watchdog", current_version="1.0.0"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.current_version = current_version
        self.api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self.release_url = f"{self.api_url}/releases/latest"
        self.logger = logger
        # Optional GitHub token for authenticated requests (reduces rate limits / access to private repos)
        self.github_token = None
        # Configurable options
        self.allow_prerelease = False
        self.asset_name_pattern = None
        self.update_channel = 'latest'
        
    def get_current_version(self):
        """Get current version of WatchDog"""
        return self.current_version
    
    def check_github_version(self):
        """Check GitHub for the latest version"""
        try:
            self.logger.info("Checking for updates...")
            headers = { 'Accept': 'application/vnd.github.v3+json' }
            if self.github_token:
                headers['Authorization'] = f"token {self.github_token}"

            response = requests.get(self.release_url, headers=headers, timeout=10)

            if response.status_code == 200:
                release_data = response.json()
                latest_version = release_data.get('tag_name', '').lstrip('v')
                return latest_version, release_data
            else:
                # If latest endpoint returns 404 (no releases), try listing releases and pick first matching one
                self.logger.warning(f"GitHub API returned status {response.status_code} for latest; attempting releases list")
                if response.status_code == 404:
                    list_url = f"{self.api_url}/releases"
                    list_resp = requests.get(list_url, headers=headers, timeout=10)
                    if list_resp.status_code == 200:
                        releases = list_resp.json()
                        for rel in releases:
                            if rel.get('draft'):
                                continue
                            if not self.allow_prerelease and rel.get('prerelease'):
                                continue
                            latest_version = rel.get('tag_name', '').lstrip('v')
                            return latest_version, rel
                    self.logger.warning(f"No releases found for {self.repo_owner}/{self.repo_name}")
                return None, None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error checking for updates: {e}")
            return None, None
        except Exception as e:
            self.logger.error(f"Error checking GitHub version: {e}")
            return None, None
    
    def compare_versions(self, latest_version):
        """Compare current version with latest version"""
        try:
            current = version.parse(self.get_current_version())
            latest = version.parse(latest_version)
            return latest > current
        except Exception as e:
            self.logger.error(f"Error comparing versions: {e}")
            return False
    
    def download_update(self, asset_url, asset_name):
        """Download update file"""
        try:
            self.logger.info(f"Downloading update: {asset_name}")
            
            # Create temp directory for download
            temp_dir = tempfile.mkdtemp(prefix="watchdog_update_")
            temp_file = os.path.join(temp_dir, asset_name)
            
            # Download with progress
            headers = {}
            if self.github_token:
                headers['Authorization'] = f"token {self.github_token}"
            response = requests.get(asset_url, headers=headers, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Show progress for large downloads
                        if total_size > 0 and downloaded % (total_size // 10) == 0:
                            progress = (downloaded / total_size) * 100
                            self.logger.info(f"Download progress: {progress:.1f}%")
            
            self.logger.info("Download completed successfully")
            return temp_file, temp_dir
            
        except Exception as e:
            self.logger.error(f"Error downloading update: {e}")
            return None, None
    
    def apply_update(self, update_file):
        """Apply the update by replacing current executable"""
        try:
            self.logger.info("Applying update...")
            # Determine current executable. If running as a frozen app (PyInstaller),
            # sys.executable is the application binary. Otherwise, we're running as a
            # script and we should not attempt to replace the Python interpreter.
            current_exe = sys.executable
            is_frozen = getattr(sys, 'frozen', False)

            # If not frozen, just launch the downloaded update and return.
            if not is_frozen:
                self.logger.info("Not a frozen executable; launching downloaded update instead of replacing runtime.")
                try:
                    subprocess.Popen([update_file], shell=False)
                    self.logger.info("Launched updater/installer successfully")
                    return True
                except Exception as e:
                    self.logger.error(f"Failed to launch update file: {e}")
                    return False

            backup_exe = current_exe + ".backup"

            # Create backup
            self.logger.info("Creating backup of current executable...")
            try:
                if os.path.exists(backup_exe):
                    os.remove(backup_exe)
                if os.path.exists(current_exe):
                    os.rename(current_exe, backup_exe)
            except Exception as e:
                self.logger.error(f"Failed to create backup: {e}")
                return False

            # Prepare helper script that will move the downloaded update into place
            # once the original executable is no longer locked, then delete backup
            helper_path = None
            try:
                if os.name == 'nt':
                    helper_path = os.path.join(os.path.dirname(update_file), 'apply_update.bat')
                    with open(helper_path, 'w', encoding='utf-8') as hb:
                        hb.write(f'@echo off\n')
                        hb.write(f'set NEW="%~1"\n')
                        hb.write(f'set TARGET="%~2"\n')
                        hb.write(f'set BACKUP="%~3"\n')
                        hb.write(':retry\n')
                        hb.write('move /Y %NEW% %TARGET% >nul 2>&1\n')
                        hb.write('if errorlevel 1 (timeout /t 1 >nul & goto retry)\n')
                        hb.write('del /f /q %BACKUP% >nul 2>&1\n')
                        hb.write('start "" %TARGET%\n')
                else:
                    helper_path = os.path.join(os.path.dirname(update_file), 'apply_update.sh')
                    with open(helper_path, 'w', encoding='utf-8') as hb:
                        hb.write('#!/bin/sh\n')
                        hb.write('NEW="$1"\n')
                        hb.write('TARGET="$2"\n')
                        hb.write('BACKUP="$3"\n')
                        hb.write('while ! mv "$NEW" "$TARGET" 2>/dev/null; do\n')
                        hb.write('  sleep 1\n')
                        hb.write('done\n')
                        hb.write('rm -f "$BACKUP" 2>/dev/null\n')
                        hb.write('chmod +x "$TARGET" 2>/dev/null\n')
                        hb.write('"$TARGET" &\n')
                    os.chmod(helper_path, 0o755)

                # Launch helper in detached mode and pass arguments: update_file, target path, backup path
                self.logger.info("Starting helper to apply the update when possible...")
                if os.name == 'nt':
                    # Use start to detach; subprocess.Popen with creationflags also works
                    subprocess.Popen(['cmd', '/c', 'start', '""', helper_path, update_file, current_exe, backup_exe], shell=False)
                else:
                    subprocess.Popen([helper_path, update_file, current_exe, backup_exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

                self.logger.info("Helper started. Exiting current process to allow replacement.")
                return True
            except Exception as e:
                self.logger.error(f"Error preparing or launching helper: {e}")
                # Attempt to restore backup if helper failed
                try:
                    if os.path.exists(backup_exe) and not os.path.exists(current_exe):
                        os.rename(backup_exe, current_exe)
                        self.logger.info("Restored original executable from backup")
                except Exception as restore_error:
                    self.logger.error(f"Failed to restore backup after helper failure: {restore_error}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error applying update: {e}")
            # Try to restore backup
            try:
                if os.path.exists(backup_exe) and os.path.exists(current_exe):
                    os.remove(current_exe)
                    os.rename(backup_exe, current_exe)
                    self.logger.info("Restored from backup")
            except Exception as restore_error:
                self.logger.error(f"Failed to restore backup: {restore_error}")
            return False
    
    def restart_application(self):
        """Restart the application properly"""
        try:
            self.logger.info("Restarting application...")
            
            # Give user time to see the message
            time.sleep(2)
            
            # Start new process
            subprocess.Popen([sys.executable] + sys.argv)
            
            # Exit current process
            self.logger.info("Update complete. New version starting...")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restarting application: {e}")
            return False
    
    def cleanup_backup(self):
        """Clean up backup file after successful restart"""
        try:
            backup_exe = sys.executable + ".backup"
            if os.path.exists(backup_exe):
                os.remove(backup_exe)
                self.logger.info("Cleaned up backup file")
        except Exception as e:
            self.logger.warning(f"Could not clean up backup: {e}")
    
    def perform_update(self, auto_confirm=False):
        """Perform complete update process"""
        try:
            # Check for new version
            latest_version, release_data = self.check_github_version()
            if not latest_version:
                self.logger.info("Could not check for updates")
                return False
            
            # Compare versions
            if not self.compare_versions(latest_version):
                self.logger.info(f"WatchDog is up to date (v{self.get_current_version()})")
                return False
            
            self.logger.info(f"New version available: v{latest_version}")
            
            # Find appropriate asset
            asset = None
            # choose asset pattern from config or default by OS
            pattern = (self.asset_name_pattern or ("windows" if os.name == 'nt' else "linux")).lower()

            for asset_data in release_data.get('assets', []):
                asset_name = asset_data.get('name', '').lower()
                if pattern in asset_name and ('.exe' in asset_name or '.zip' in asset_name or asset_name.endswith('.msi')):
                    asset = asset_data
                    break
            
            if not asset:
                self.logger.warning("No suitable update asset found for this platform")
                return False
            
            # Confirm update
            if not auto_confirm:
                try:
                    confirm = input(f"Update to v{latest_version}? (y/N): ")
                    if confirm.lower() != 'y':
                        self.logger.info("Update cancelled by user")
                        return False
                except Exception as e:
                    # If input fails, proceed with update
                    self.logger.info("Proceeding with update...")
            
            # Download update
            update_file, temp_dir = self.download_update(asset['browser_download_url'], asset['name'])
            if not update_file:
                return False
            
            # Apply update
            if self.apply_update(update_file):
                # Clean up temp files (note: helper may still be running from temp_dir)
                try:
                    import shutil
                    # Do not remove temp_dir immediately on Windows if helper uses it; attempt gentle cleanup
                    if os.name != 'nt':
                        shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception:
                    pass

                print("✅ Update helper launched. Exiting to allow installer to run.")
                # Exit current process to allow helper to replace and start new executable
                try:
                    sys.exit(0)
                except SystemExit:
                    return True
            else:
                # Clean up on failure
                try:
                    import shutil
                    if update_file and os.path.exists(update_file):
                        os.remove(update_file)
                    if temp_dir and os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception as e:
                    pass
                return False
                
        except Exception as e:
            self.logger.error(f"Error during update process: {e}")
            return False

def _load_config_values():
    """Load repo and version info from config/settings.json if available."""
    try:
        # When frozen by PyInstaller, use sys._MEIPASS (temporary folder where bundle is unpacked).
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        else:
            # Running as script
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        config_path = os.path.join(base_path, 'config', 'settings.json')
        logger.debug(f"Looking for config at: {config_path}")
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8-sig') as f:
                cfg = json.load(f)
                repo_owner = cfg.get('repo_owner') or cfg.get('repository_owner')
                repo_name = cfg.get('repo_name') or cfg.get('repository_name')
                current_version = cfg.get('version')
                github_token = cfg.get('github_token')
                allow_prerelease = bool(cfg.get('allow_prerelease', False))
                asset_name_pattern = cfg.get('asset_name_pattern')
                update_channel = cfg.get('update_channel')
                logger.debug(f"Loaded config: owner={repo_owner}, repo={repo_name}, version={current_version}")
                return repo_owner, repo_name, current_version, github_token, allow_prerelease, asset_name_pattern, update_channel
        else:
            logger.warning(f"Config file not found at: {config_path}")
    except Exception as e:
        logger.error(f"Error loading config: {e}")
    return None, None, None, None, False, None, None


def create_updater_from_config(default_owner='yourusername', default_name='watchdog', default_version='1.0.0'):
    repo_owner, repo_name, current_version, github_token, allow_prerelease, asset_name_pattern, update_channel = _load_config_values()
    if not repo_owner:
        repo_owner = default_owner
    if not repo_name:
        repo_name = default_name
    if not current_version:
        current_version = default_version
    gh = GitHubUpdater(repo_owner=repo_owner, repo_name=repo_name, current_version=current_version)
    # token precedence: config -> env var
    token = github_token or os.environ.get('GITHUB_TOKEN')
    if token:
        gh.github_token = token
    if allow_prerelease:
        gh.allow_prerelease = True
    if asset_name_pattern:
        gh.asset_name_pattern = asset_name_pattern
    if update_channel:
        gh.update_channel = update_channel
    return gh


# Global updater instance created from configuration (falls back to sensible defaults)
updater = create_updater_from_config(default_owner="LogicFordge961", default_name="WatchDog", default_version="1.0.0")

def check_for_updates(auto_update=False):
    """Check for updates and optionally auto-update"""
    try:
        if auto_update:
            return updater.perform_update(auto_confirm=True)
        else:
            latest_version, _ = updater.check_github_version()
            if latest_version and updater.compare_versions(latest_version):
                print(f"🔄 Update available: v{latest_version}")
                print("Run 'update' command to install the latest version")
                return True
            elif latest_version:
                print(f"✅ WatchDog is up to date (v{updater.get_current_version()})")
                return False
    except Exception as e:
        logger.error(f"Error checking for updates: {e}")
        return False
    return False
