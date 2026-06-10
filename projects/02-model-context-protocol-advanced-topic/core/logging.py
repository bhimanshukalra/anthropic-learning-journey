import logging
import os
import sys


def configure_logging() -> None:
    # Read the level at startup so `.env` values loaded by the app can control it.
    log_level = os.getenv("MCP_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        # MCP servers use stdout for protocol messages, so logs must go to stderr.
        stream=sys.stderr,
    )


def get_logger(name: str) -> logging.Logger:
    # Named loggers make it easier to see which file produced each log line.
    return logging.getLogger(name)
