
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from crispit.db.base import Base

if TYPE_CHECKING:
    from crispit.models.delivery_attempt import DeliveryAttempt
    from crispit.models.delivery_item import DeliveryItem
    from crispit.models.user import User


class Delivery(Base):
    """Represents one intended delivery to a user."""

    __tablename__ = "deliveries"

    __table_args__ = (
        # Prevent the same intended delivery from being created twice.
        UniqueConstraint(
            "delivery_key",
            name="uq_deliveries_delivery_key",
        ),

        CheckConstraint(
            "delivery_policy IN ('immediate', 'daily')",
            name="ck_deliveries_policy",
        ),

        CheckConstraint(
            "output_format IN ('text', 'pdf')",
            name="ck_deliveries_output_format",
        ),

        CheckConstraint(
            "status IN ('pending', 'sending', 'sent', 'failed')",
            name="ck_deliveries_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Identifies this delivery across retries and scheduler runs.
    delivery_key: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    # Save the selected settings so later preference changes
    # do not unexpectedly change an existing delivery.
    delivery_policy: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    output_format: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # Store the actual planned delivery time in UTC.
    # Immediate deliveries may not need a scheduled time.
    scheduled_for: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default=text("'pending'"),
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

    # The recipient of this delivery.
    user: Mapped["User"] = relationship(
        back_populates="deliveries",
    )

    # One delivery can contain several summaries.
    items: Mapped[list["DeliveryItem"]] = relationship(
        back_populates="delivery",
        order_by="DeliveryItem.position",
    )

    # Keep the history of attempts to send this delivery.
    attempts: Mapped[list["DeliveryAttempt"]] = relationship(
        back_populates="delivery",
        order_by="DeliveryAttempt.attempt_number",
    )
