from fastapi import FastAPI

from crispit.api.routes.health import router as health_router
from crispit.core.config import get_settings
from crispit.core.logging_config import configure_logging, get_logger


def create_app() -> FastAPI:
    """Create and configure the Crispit FastAPI application."""

    settings = get_settings()
    configure_logging(settings.log_level)

    application = FastAPI(title=settings.app_name)
    application.include_router(health_router)

    logger = get_logger(__name__)
    logger.info(
        "Crispit application configured for the %s environment",
        settings.app_environment,
    )

    return application


app = create_app()