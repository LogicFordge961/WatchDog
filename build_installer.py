#!/usr/bin/env python3
"""
Build script for WatchDog installer
"""

import os
import subprocess
import sys
import shutil

def create_placeholder_images(installer_dir):
    """Create placeholder icon and bitmap files"""
    try:
        from PIL import Image
        
        # Create a 32x32 white icon
        icon_path = os.path.join(installer_dir, 'icon.ico')
        img = Image.new('RGBA', (32, 32), (255, 255, 255, 255))
        img.save(icon_path, 'ICO')
        
        # Create header bitmap (200x60, blue gradient)
        header_path = os.path.join(installer_dir, 'header.bmp')
        header_img = Image.new('RGB', (200, 60), (0, 120, 215))
        header_img.save(header_path, 'BMP')
        
        # Create wizard bitmap (164x314, white)
        wizard_path = os.path.join(installer_dir, 'wizard.bmp')
        wizard_img = Image.new('RGB', (164, 314), (255, 255, 255))
        wizard_img.save(wizard_path, 'BMP')
        
        return True
    except ImportError:
        # Fallback: create minimal valid binary files
        # Minimal 32x32 ICO file (1x1 white pixel centered)
        icon_data = bytearray(
            b'\x00\x00\x01\x00\x01\x00\x20\x20\x00\x00\x01\x00\x20\x00'
            b'\x30\x00\x00\x00\x16\x00\x00\x00'
            b'\x28\x00\x00\x00\x20\x00\x00\x00\x40\x00\x00\x00\x01\x00\x20\x00'
            b'\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff'
            + b'\x00' * 1024  # Padding
        )
        
        icon_path = os.path.join(installer_dir, 'icon.ico')
        with open(icon_path, 'wb') as f:
            f.write(icon_data)
        
        # Minimal BMP file (1x1 white pixel)
        bmp_data = bytearray(
            b'BM'  # Signature
            b'\x46\x00\x00\x00'  # File size (70 bytes)
            b'\x00\x00\x00\x00'  # Reserved
            b'\x36\x00\x00\x00'  # Offset to pixel data (54 bytes)
            # BITMAPINFOHEADER
            b'\x28\x00\x00\x00'  # Header size (40 bytes)
            b'\x01\x00\x00\x00'  # Width (1)
            b'\x01\x00\x00\x00'  # Height (1)
            b'\x01\x00'          # Planes (1)
            b'\x18\x00'          # Bits per pixel (24)
            b'\x00\x00\x00\x00'  # Compression (none)
            b'\x00\x00\x00\x00'  # Image size
            b'\x00\x00\x00\x00'  # X pixels per meter
            b'\x00\x00\x00\x00'  # Y pixels per meter
            b'\x00\x00\x00\x00'  # Colors used
            b'\x00\x00\x00\x00'  # Important colors
            # Pixel data (white)
            b'\xff\xff\xff'      # BGR white pixel
        )
        
        header_path = os.path.join(installer_dir, 'header.bmp')
        wizard_path = os.path.join(installer_dir, 'wizard.bmp')
        
        with open(header_path, 'wb') as f:
            f.write(bmp_data)
        with open(wizard_path, 'wb') as f:
            f.write(bmp_data)
        
        return False

def build_installer():
    """Build the NSIS installer"""

    # Check if NSIS is installed
    nsis_paths = [
        r"C:\Program Files (x86)\NSIS\makensis.exe",
        r"C:\Program Files\NSIS\makensis.exe",
        "makensis.exe"  # In PATH
    ]

    makensis_path = None
    for path in nsis_paths:
        try:
            result = subprocess.run([path, '/VERSION'], capture_output=True, text=True)
            if result.returncode == 0:
                makensis_path = path
                print(f"✅ Found NSIS at: {path}")
                break
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue

    if not makensis_path:
        print("❌ NSIS not found. Please install NSIS from https://nsis.sourceforge.io/")
        print("   Or add makensis.exe to your PATH")
        return False

    # Build the executable first
    print("🔨 Building WatchDog executable...")
    try:
        subprocess.run([sys.executable, 'build_exe.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build executable: {e}")
        return False

    # Check if executable was created
    exe_path = os.path.join('dist', 'WatchDog.exe')
    if not os.path.exists(exe_path):
        print("❌ WatchDog.exe not found in dist folder")
        return False

    # Copy required files to installer directory
    installer_dir = 'installer'
    os.makedirs(installer_dir, exist_ok=True)

    # Copy executable
    shutil.copy(exe_path, os.path.join(installer_dir, 'WatchDog.exe'))

    # Copy config and docs
    shutil.copy('config/settings.json', installer_dir)
    shutil.copy('LICENSE', installer_dir)
    shutil.copy('README.md', installer_dir)

    # Create placeholder images (always recreate to ensure they're valid)
    print("⚠️  Creating placeholder images...")
    create_placeholder_images(installer_dir)

    # Build installer
    print("📦 Building installer...")
    installer_script = os.path.join(installer_dir, 'installer.nsi')
    # makensis interprets relative paths based on the current working directory.  When
    # specifying cwd=installer_dir we should pass a script path that is either
    # absolute or relative to that directory.  The previous version passed
    # "installer\\installer.nsi" while already in the installer directory, causing
    # makensis to look for a nested path and fail.
    #
    # Use the basename when running with cwd, or simply call makensis with the
    # absolute script path and no cwd.  We'll do the former for simplicity.
    script_to_build = os.path.basename(installer_script)
    try:
        subprocess.run([makensis_path, script_to_build], check=True, cwd=installer_dir)
        print("✅ Installer built successfully: installer/WatchDog_Installer.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build installer: {e}")
        return False

if __name__ == '__main__':
    success = build_installer()
    sys.exit(0 if success else 1)