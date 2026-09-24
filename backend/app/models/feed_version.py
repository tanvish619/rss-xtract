import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FeedVersion(Base):
    __tablename__ = "feed_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    feed_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False
    )

    version_major: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )

    version_minor: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    config_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )

    config_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    script_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="created",
        nullable=False
    )

    execution_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    last_execution_at: Mapped[datetime | None] = mapped_column(
        DateTime
    )

    last_success_at: Mapped[datetime | None] = mapped_column(
        DateTime
    )

    last_error: Mapped[str | None] = mapped_column(
        String
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )