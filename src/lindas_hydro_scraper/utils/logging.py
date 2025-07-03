"""Logging configuration utilities."""

import logging
import sys
from pathlib import Path

from ..core.constants import LOG_FORMAT


def setup_logging(
    level: str = "INFO",
    log_file: Path | None = None,
    format_string: str = LOG_FORMAT,
) -> None:
    """Configure application logging.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR).
        log_file: Optional file path for log output.
        format_string: Log message format.
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Configure handlers
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format=format_string,
        handlers=handlers,
        force=True,  # Override any existing configuration
    )

    # Set specific loggers
    logging.getLogger("SPARQLWrapper").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
