import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from crispit.models.source_subscription import SourceSubscription
    from crispit.models.video import Video

from crispit.db.base import Base


class Source(Base):
    __tablename__ = "sources"

    __table_args__ = (
        UniqueConstraint(
            "youtube_channel_id",
            name="uq_sources_youtube_channel_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    youtube_channel_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    subscriptions: Mapped[list["SourceSubscription"]] = relationship(
        back_populates="source",
    )

    videos: Mapped[list["Video"]] = relationship(
        back_populates="source",
    )