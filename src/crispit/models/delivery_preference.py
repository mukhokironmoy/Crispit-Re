
import uuid
from datetime import datetime, time
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Time,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from crispit.db.base import Base

if TYPE_CHECKING:
    from crispit.models.user import User


class DeliveryPreference(Base):
    """Stores a user's default summary delivery settings."""

    __tablename__ = "delivery_preferences"

    __table_args__ = (
        # Each user has one set of default delivery preferences.
        UniqueConstraint(
            "user_id",
            name="uq_delivery_preferences_user_id",
        ),

        # Only support immediate and daily delivery in V1.
        CheckConstraint(
            "delivery_policy IN ('immediate', 'daily')",
            name="ck_delivery_preferences_policy",
        ),

        # Keep the initial output formats limited to text and PDF.
        CheckConstraint(
            "output_format IN ('text', 'pdf')",
            name="ck_delivery_preferences_output_format",
        ),

        # Daily delivery requires a scheduled time.
        # Immediate delivery does not need one.
        CheckConstraint(
            "(delivery_policy = 'daily' AND delivery_time IS NOT NULL) OR "
            "(delivery_policy = 'immediate' AND delivery_time IS NULL)",
            name="ck_delivery_preferences_time",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Delete these preferences if their user account is deleted.
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Immediate summaries are sent when ready.
    # Daily summaries wait until the configured delivery time.
    delivery_policy: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="immediate",
        server_default=text("'immediate'"),
    )

    # Select how the summary should be presented on Telegram.
    output_format: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="text",
        server_default=text("'text'"),
    )

    # Use an IANA timezone name to handle local times correctly.
    timezone: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="UTC",
        server_default=text("'UTC'"),
    )

    # This is the user's local clock time, not a UTC timestamp.
    delivery_time: Mapped[time | None] = mapped_column(
        Time(timezone=False),
        nullable=True,
    )

    # Users can pause automated deliveries without losing their settings.
    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Access the owner through preference.user.
    user: Mapped["User"] = relationship(
        back_populates="delivery_preference",
    )
