from typing import Literal

from fastapi import APIRouter, status
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response returned by the application liveness check."""

    status: Literal["ok"]


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