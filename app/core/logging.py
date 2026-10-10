"""
Centralised logging configuration.

Usage (in any module):
    from app.core.logging import get_logger

    logger = get_logger(__name__)
    logger.info("Something happened")

Log levels and what they mean here:
    DEBUG    – Fine-grained diagnostic info (DB queries, function entry/exit).
    INFO     – Normal operational events (user created, request received).
    WARNING  – Unexpected but recoverable situations (duplicate signup attempt).
    ERROR    – Failures that need attention (DB commit failed, unhandled exception).
    CRITICAL – Application cannot continue (startup failure).
"""

import logging
import sys
from logging import Logger

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# Internal flag — ensures setup() is only called once
_configured = False


def setup_logging(level: str | None = None) -> None:

    # Configure the root logger.
    global _configured
    if _configured:
        return

    import os

    resolved_level = level or os.getenv("LOG_LEVEL", "DEBUG").upper()

    formatter = logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT)

    # --- Console handler (stdout so Docker / uvicorn capture it cleanly) ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # --- Root logger --------------------------------------------------------
    root_logger = logging.getLogger()
    root_logger.setLevel(resolved_level)

    # Avoid adding duplicate handlers if the logger already has some
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)

    # Quieten noisy third-party loggers so they don't drown our output
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    _configured = True


def get_logger(name: str) -> Logger:
    # Get a logger for the given module name.
    return logging.getLogger(name)
