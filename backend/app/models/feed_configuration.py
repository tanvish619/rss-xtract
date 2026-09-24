import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FeedConfiguration(Base):
    __tablename__ = "feed_configurations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    feed_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False
    )

    item_selector: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    title_selector: Mapped[str | None] = mapped_column(Text)
    link_selector: Mapped[str | None] = mapped_column(Text)
    date_selector: Mapped[str | None] = mapped_column(Text)
    description_selector: Mapped[str | None] = mapped_column(Text)
    image_selector: Mapped[str | None] = mapped_column(Text)
    author_selector: Mapped[str | None] = mapped_column(Text)
    category_selector: Mapped[str | None] = mapped_column(Text)

    pagination_selector: Mapped[str | None] = mapped_column(Text)

    max_items: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        default=None
    )

    rendering_mode: Mapped[str] = mapped_column(
        String(30),
        default="request"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )