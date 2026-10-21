
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from crispit.db.base import Base

if TYPE_CHECKING:
    from crispit.models.delivery import Delivery
    from crispit.models.summary import Summary


class DeliveryItem(Base):
    """Links one summary to an intended delivery."""

    __tablename__ = "delivery_items"

    __table_args__ = (
        # Include a summary only once in the same delivery.
        UniqueConstraint(
            "delivery_id",
            "summary_id",
            name="uq_delivery_items_delivery_summary",
        ),

        # Each summary has a fixed position within a batch.
        UniqueConstraint(
            "delivery_id",
            "position",
            name="uq_delivery_items_delivery_position",
        ),

        CheckConstraint(
            "position > 0",
            name="ck_delivery_items_position",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Delete these links if their delivery is deleted.
    # The saved summaries themselves are not deleted.
    delivery_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("deliveries.id", ondelete="CASCADE"),
        nullable=False,
    )

    summary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("summaries.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Controls the order of summaries in a daily digest.
    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    delivery: Mapped["Delivery"] = relationship(
        back_populates="items",
    )

    summary: Mapped["Summary"] = relationship(
        back_populates="delivery_items",
    )
