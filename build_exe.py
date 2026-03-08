import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    '--name=WatchDog',
    '--onefile',
    '--console',
    '--clean',
    'watchdog.py'
])
