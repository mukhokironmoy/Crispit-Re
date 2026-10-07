from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from crispit.db.dependencies import get_db


class HealthResponse(BaseModel):
    """Response returned by the application liveness check."""

    status: Literal["ok"]

class ReadinessResponse(BaseModel):
    """Response returned by the application readiness check."""

    status: Literal["ready"]


router = APIRouter(prefix="/health", tags=["health"])

@router.get(
    "/live",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Check application liveness",
)
async def check_liveness() -> HealthResponse:
    """Confirm that the Crispit application process is running."""

    return HealthResponse(status="ok")


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Check application readiness",
)
async def check_readiness(
    db: Annotated[Session, Depends(get_db)],
) -> ReadinessResponse:
    """Confirm that Crispit can reach its required database."""

    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc

    return ReadinessResponse(status="ready")