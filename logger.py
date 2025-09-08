# logger.py
import logging

# ANSI escape codes for colors
LOG_COLORS = {
    logging.DEBUG: "\033[32m",    # Dark Green
    logging.INFO: "\033[36m",     # Cyan
    logging.WARNING: "\033[33m",  # Yellow
    logging.ERROR: "\033[31m",    # Red
    logging.CRITICAL: "\033[41m", # Red background
}
RESET_COLOR = "\033[0m"

class ColorFormatter(logging.Formatter):
    def format(self, record):
        log_color = LOG_COLORS.get(record.levelno, "")
        record.levelname = f"{log_color}{record.levelname}{RESET_COLOR}"
        record.msg = f"{log_color}{record.msg}{RESET_COLOR}"
        return super().format(record)

# Create or get logger
logger = logging.getLogger("jarvis_logger")
logger.setLevel(logging.DEBUG)  # You can change this to INFO if preferred

# Prevent adding duplicate handlers if this gets imported multiple times
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = ColorFormatter("[%(asctime)s] %(levelname)s - %(message)s", "%H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
