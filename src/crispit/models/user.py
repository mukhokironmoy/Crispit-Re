import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from crispit.models.source_subscription import SourceSubscription
    from crispit.models.summary_mode import SummaryMode
    from crispit.models.telegram_identity import TelegramIdentity

from crispit.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    telegram_identities: Mapped[list["TelegramIdentity"]] = relationship(
        back_populates="user",
    )

    summary_modes: Mapped[list["SummaryMode"]] = relationship(
        back_populates="owner",
    )

    source_subscriptions: Mapped[list["SourceSubscription"]] = relationship(
        back_populates="user",
    )