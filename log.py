import logging
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.DEBUG:
            record.levelname = f"{Fore.CYAN}{record.levelname}{Style.RESET_ALL}"
        elif record.levelno == logging.INFO:
            record.levelname = f"{Fore.GREEN}{record.levelname}{Style.RESET_ALL}"
        elif record.levelno == logging.WARNING:
            record.levelname = f"{Fore.YELLOW}{record.levelname}{Style.RESET_ALL}"
        elif record.levelno == logging.ERROR:
            record.levelname = f"{Fore.RED}{record.levelname}{Style.RESET_ALL}"
        elif record.levelno == logging.CRITICAL:
            record.levelname = f"{Fore.MAGENTA}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)

def setup_logger(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a custom logger with colourful text.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        formatter = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger