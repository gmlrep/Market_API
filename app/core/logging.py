import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    level = settings.server.LOGGING_LEVEL
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(asctime)s - %(name)s - %(message)s",
        stream=sys.stdout,
        force=True,
    )
