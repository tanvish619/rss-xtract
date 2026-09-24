import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, SmallInteger, Text, String
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(Text, nullable=False)

    source_type: Mapped[str] = mapped_column(
        String(30),
        default="web",
        nullable=False
    )

    categories: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text)
    )

    country_code: Mapped[str | None] = mapped_column(
        String(2)
    )

    language_code: Mapped[str | None] = mapped_column(
        String(10)
    )

    geographic_scope: Mapped[str | None] = mapped_column(
        String(20)
    )

    publishing_volume: Mapped[str | None] = mapped_column(
        String(20)
    )

    priority: Mapped[int] = mapped_column(
        SmallInteger,
        default=3
    )

    proxy_required: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    proxy_used: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    scraping_strategy: Mapped[str | None] = mapped_column(
        String(30)
    )

    source_from: Mapped[str] = mapped_column(
        String(20),
        default="public"
    )

    active_status: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    deactivation_reason: Mapped[str | None] = mapped_column(
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