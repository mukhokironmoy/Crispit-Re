
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from crispit.db.base import Base

if TYPE_CHECKING:
    from crispit.models.delivery_item import DeliveryItem
    from crispit.models.processing_job import ProcessingJob
    from crispit.models.summary_mode import SummaryMode
    from crispit.models.video import Video


class Summary(Base):
    """Stores validated summary content for reuse across delivery formats."""

    __tablename__ = "summaries"

    __table_args__ = (
        # A processing job can produce only one saved summary.
        # Regenerating a summary requires a new processing job.
        UniqueConstraint(
            "processing_job_id",
            name="uq_summaries_processing_job_id",
        ),

        # Schema versions start at 1, allowing future changes to the JSON format.
        CheckConstraint(
            "schema_version > 0",
            name="ck_summaries_schema_version",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Link the summary to the job that generated it.
    processing_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("processing_jobs.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Keep direct references to the video and mode for easier searching.
    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("videos.id", ondelete="RESTRICT"),
        nullable=False,
    )

    summary_mode_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("summary_modes.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Identifies which version of our JSON notes structure was used.
    schema_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default=text("1"),
    )

    # Store structured notes instead of Telegram-specific Markdown.
    # The same JSON can later be rendered as Telegram text, PDF, or HTML.
    content: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )

    # Record which LLM generated the summary for debugging and comparison.
    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    model_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    # PostgreSQL automatically records when the summary is first saved.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Allow SQLAlchemy to access related records as Python objects.
    # For example: summary.video or summary.processing_job.
    processing_job: Mapped["ProcessingJob"] = relationship(
        back_populates="summary",
    )

    video: Mapped["Video"] = relationship(
        back_populates="summaries",
    )

    summary_mode: Mapped["SummaryMode"] = relationship(
        back_populates="summaries",
    )

    # A summary may be included in several intended deliveries.
    delivery_items: Mapped[list["DeliveryItem"]] = relationship(
        back_populates="summary",
    )
