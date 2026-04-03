from loguru import logger
import sys
from pathlib import Path

LOGS_DIR = Path.home() / "jarvis" / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logger.remove()
logger.add(sys.stderr, level="INFO",
           format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan> | {message}")
logger.add(LOGS_DIR / "{time:YYYY-MM-DD}.log",
           rotation="1 day", retention="30 days", level="DEBUG")
