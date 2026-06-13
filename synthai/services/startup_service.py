"""Service Layer — application startup and initialisation workflow."""

import os

from synthai.data.config.settings import ensure_dirs
from synthai.data.database import Database


class StartupService:
    """Coordinates startup tasks: directory setup, DB schema init, env vars.

    This service encapsulates all data-layer initialisation so the API layer
    never needs to import from synthai.data.* directly.
    """

    @staticmethod
    def initialize() -> None:
        os.environ["JOBLIB_SINGLE_THREADED"] = "1"
        os.environ["LOKY_MAX_CPU_COUNT"] = "1"
        ensure_dirs()
        Database.init_db()
