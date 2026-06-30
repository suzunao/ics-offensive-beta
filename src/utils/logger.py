"""
Logging utilities for ICS Offensive MCP.
"""
import logging
from typing import Optional


def setup_logger(name: str = "ics-offensive-mcp", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name or "ics-offensive-mcp")
