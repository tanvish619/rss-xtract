import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FeedRun(Base):
    __tablename__ = "feed_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    feed_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    article_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    duration_ms: Mapped[int | None] = mapped_column(
        Integer
    )

    error_message: Mapped[str | None] = mapped_column(
        Text
    )

    log_path: Mapped[str | None] = mapped_column(
        String(500)
    )