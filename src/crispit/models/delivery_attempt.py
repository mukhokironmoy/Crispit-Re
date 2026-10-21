
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from crispit.db.base import Base

if TYPE_CHECKING:
    from crispit.models.delivery import Delivery


class DeliveryAttempt(Base):
    """Records one attempt to send an existing delivery."""

    __tablename__ = "delivery_attempts"

    __table_args__ = (
        # Retry numbers must be unique within a delivery.
        UniqueConstraint(
            "delivery_id",
            "attempt_number",
            name="uq_delivery_attempts_delivery_number",
        ),

        CheckConstraint(
            "status IN ('pending', 'sending', 'sent', 'failed')",
            name="ck_delivery_attempts_status",
        ),

        CheckConstraint(
            "attempt_number > 0",
            name="ck_delivery_attempts_attempt_number",
        ),

        # Helps us find recent attempts for a delivery.
        Index(
            "ix_delivery_attempts_delivery_created",
            "delivery_id",
            "created_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Each retry belongs to the same intended delivery.
    delivery_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("deliveries.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Telegram is our initial delivery platform.
    platform: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="telegram",
        server_default=text("'telegram'"),
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default=text("'pending'"),
    )

    # First attempt = 1, next retry = 2, and so on.
    attempt_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Save Telegram's message ID when a message is sent.
    # One delivery can produce multiple messages, so this
    # field is only a simple reference for now.
    telegram_message_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    # Keep the failure reason separate from the summary.
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Access the delivery and its recipient through the ORM.
    delivery: Mapped["Delivery"] = relationship(
        back_populates="attempts",
    )
