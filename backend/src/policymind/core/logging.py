"""Structured logging configuration."""

import logging
import sys


def setup_logging(*, level: int = logging.INFO) -> None:
    """Configure structured JSON-line logging for production, readable for dev."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)
