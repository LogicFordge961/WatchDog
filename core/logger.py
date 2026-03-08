# core/logger.py
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import sys

if getattr(sys, 'frozen', False):
    LOG_DIR = os.path.join(os.path.dirname(sys.executable), "data/logs")
else:
    LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'logs')

class DiscordLogFilter(logging.Filter):
    """Filter to specifically target Discord spam"""
    def filter(self, record):
        # Allow critical Discord errors through, but filter out verbose connection logs
        if hasattr(record, 'name') and 'discord' in record.name.lower():
            # Allow ERROR and CRITICAL level messages
            if record.levelno >= logging.ERROR:
                return True
            # Filter out INFO and DEBUG level Discord messages
            elif record.levelno < logging.WARNING:
                # But allow specific important messages
                important_messages = [
                    'error', 'failed', 'exception', 'critical'
                ]
                message_lower = getattr(record, 'message', '').lower()
                if any(keyword in message_lower for keyword in important_messages):
                    return True
                return False
        return True

def setup_logging(log_level="INFO"):
    """Setup logging with targeted Discord filtering"""
    log_dir = "data/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Clear existing handlers
    logging.root.handlers = []
    logging.root.setLevel(getattr(logging, log_level))
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler (captures everything including Discord logs)
    log_file = os.path.join(log_dir, f"watchdog_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=20*1024*1024,  # 20MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler with Discord filter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.addFilter(DiscordLogFilter())  # Apply Discord filter
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Set specific log levels for noisy libraries
    noisy_libraries = [
        ('websockets', logging.WARNING),
        ('urllib3', logging.WARNING),
        ('httpx', logging.WARNING),
        ('charset_normalizer', logging.ERROR),
        ('asyncio', logging.WARNING)
    ]
    
    for lib, level in noisy_libraries:
        logging.getLogger(lib).setLevel(level)

def get_logger(name):
    """Get configured logger"""
    return logging.getLogger(name)
