import os

from crispit.core.config import Settings, get_settings

settings = Settings()

if settings.test_database_url is None:
    raise RuntimeError(
        "CRISPIT_TEST_DATABASE_URL must be set to run integration tests."
    )

os.environ["CRISPIT_DATABASE_URL"] = settings.test_database_url

get_settings.cache_clear()