
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from crispit.db.base import Base

if TYPE_CHECKING:
    from crispit.models.summary import Summary
    from crispit.models.summary_mode import SummaryMode
    from crispit.models.user import User
    from crispit.models.video import Video


class ProcessingJob(Base):
    """Tracks a video processing job, its status, and retry attempts."""

    __tablename__ = "processing_jobs"

    __table_args__ = (
        # Only allow these four job statuses.
        CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed')",
            name="ck_processing_jobs_status",
        ),
        # Keep retry counts within valid limits.
        CheckConstraint(
            "attempt_count >= 0 AND max_attempts > 0 "
            "AND attempt_count <= max_attempts",
            name="ck_processing_jobs_attempts",
        ),
        # Speed up searches for pending jobs ready to run.
        Index(
            "ix_processing_jobs_claimable",
            "available_at",
            postgresql_where=text("status = 'pending'"),
        ),
        # Speed up checks for running jobs with expired locks.
        Index(
            "ix_processing_jobs_running_lease",
            "locked_until",
            postgresql_where=text("status = 'running'"),
        ),
    )

    # Unique ID for each processing job.
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Video this job processes.
    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("videos.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Summary mode used for processing.
    summary_mode_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("summary_modes.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # User who requested the job, if any.
    requested_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Current job status. New jobs start as pending.
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default=text("'pending'"),
    )

    # Number of processing attempts made.
    attempt_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )

    # Maximum number of attempts allowed.
    max_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
        server_default=text("3"),
    )

    # Earliest time the job can be picked up.
    available_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Time a worker picked up the job.
    claimed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Time until which the worker holds the job lock.
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Time the job finished successfully.
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Error message from the last failed attempt.
    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Time the job was created.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Time the job was last updated.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Related video, summary mode, and requesting user.
    video: Mapped["Video"] = relationship(
        back_populates="processing_jobs",
    )

    summary_mode: Mapped["SummaryMode"] = relationship(
        back_populates="processing_jobs",
    )

    requested_by_user: Mapped["User | None"] = relationship(
        back_populates="processing_jobs",
    )

    # A successful job produces at most one saved summary.
    summary: Mapped["Summary | None"] = relationship(
        back_populates="processing_job",
        uselist=False,
    )
