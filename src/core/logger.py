import sys

from loguru import logger


def setup_logging():
    logger.remove()
    logs_format: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:"
        "<cyan>{function}</cyan>:"
        "<cyan>{line}</cyan> - <level>{message}</level>"
    )
    logger.add(
        sys.stdout,
        colorize=True,
        format=logs_format,
        level="INFO",
    )
