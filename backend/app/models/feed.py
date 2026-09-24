import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Feed(Base):
    __tablename__ = "feeds"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text
    )

    current_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True)
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="created",
        nullable=False
    )

    refresh_interval_seconds: Mapped[int] = mapped_column(
        Integer,
        default=1800
    )

    last_run_at: Mapped[datetime | None] = mapped_column(
        DateTime
    )

    last_success_at: Mapped[datetime | None] = mapped_column(
        DateTime
    )

    last_error: Mapped[str | None] = mapped_column(
        Text
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )