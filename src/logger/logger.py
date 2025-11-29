from loguru import logger
from shared.path_manager import PathManager
from pathlib import Path
import sys
import inspect

# Base logs directory
LOG_DIR = PathManager().log_dir
LOG_DIR.mkdir(exist_ok=True)


def get_logger():
    """
    Returns a logger configured for the calling module.
    Each module logs to its own file, rotated daily.
    """
    # Get the name of the calling module (file name without extension)
    caller_name = inspect.stack()[1].filename
    app_name = Path(caller_name).stem

    log_path = LOG_DIR / f"{app_name}.log"

    # Remove old handlers to avoid duplicate logs in multi-import scenarios
    logger.remove()

    # Console output (nice formatting)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
        level="DEBUG",
    )

    # File output with rotation
    logger.add(
        log_path,
        rotation="00:00",  # new file every day at midnight
        retention="7 days",  # keep logs for a week
        compression="zip",  # optional: compress old logs
        level="WARNING",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )

    return logger
