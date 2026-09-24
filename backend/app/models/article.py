import uuid
from datetime import datetime

from sqlalchemy import DateTime, Text, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    feed_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False
    )

    guid: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    title: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    link: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text)
    author: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(Text)

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime
    )

    content_hash: Mapped[str | None] = mapped_column(
        String(64)
    )

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )