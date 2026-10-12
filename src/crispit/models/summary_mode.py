import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from crispit.db.base import Base

if TYPE_CHECKING:
    from crispit.models.user import User


class SummaryMode(Base):
    __tablename__ = "summary_modes"

    __table_args__ = (
        CheckConstraint(
            "(is_builtin = true AND owner_user_id IS NULL) OR "
            "(is_builtin = false AND owner_user_id IS NOT NULL)",
            name="ck_summary_modes_ownership",
        ),
        Index(
            "uq_summary_modes_builtin_key",                         # Among built-in modes, every mode_key must be unique.
            "mode_key",
            unique=True,
            postgresql_where=text("is_builtin = true"),
        ),
        Index(
            "uq_summary_modes_owner_key",                           # two different users can have the same mode key, but the same user cannot create two custom modes with identical keys.
            "owner_user_id",
            "mode_key",
            unique=True,
            postgresql_where=text("is_builtin = false"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )

    mode_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    prompt_template: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    is_builtin: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

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

    owner: Mapped["User | None"] = relationship(
        back_populates="summary_modes",
    )
