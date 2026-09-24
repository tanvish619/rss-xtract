from uuid import uuid4
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.feed_schema import FeedCreateRequest, BuildFeedRequest
from app.models.feed import Feed
from app.models.source import Source
from app.models.feed_version import FeedVersion
from app.models.feed_configuration import FeedConfiguration
from app.services.config_hash import calculate_config_hash
from app.services.scraper_generator import generate_scraper
from app.services.feed_worker import run_feed_task


router = APIRouter(
    prefix="/feeds",
    tags=["Feeds"]
)


@router.post("/")
def create_feed(
    request: FeedCreateRequest,
    db: Session = Depends(get_db)
):
    feed = Feed(
        id=uuid4(),
        source_id=request.source_id,
        name=request.name,
        description=request.description,
        refresh_interval_seconds=request.refresh_interval_seconds
    )

    db.add(feed)
    db.commit()
    db.refresh(feed)

    return {
        "message": "Feed created",
        "feed_id": str(feed.id)
    }


@router.post("/build")
def build_feed(
    request: BuildFeedRequest,
    db: Session = Depends(get_db)
):
    url = str(request.url).rstrip("/")

    configuration = request.configuration.model_dump()

    config_hash = calculate_config_hash(
        url,
        configuration
    )

    # Reuse an existing identical configuration
    existing_version = (
        db.query(FeedVersion)
        .filter(FeedVersion.config_hash == config_hash)
        .first()
    )

    if existing_version:
        feed = (
            db.query(Feed)
            .filter(Feed.id == existing_version.feed_id)
            .first()
        )

        if not feed:
            raise HTTPException(
                status_code=500,
                detail="Existing feed version points to a missing feed"
            )

        task = run_feed_task.delay(str(existing_version.id))

        return {
            "feed_id": str(feed.id),
            "feed_version_id": str(existing_version.id),
            "version": f"v{existing_version.version_major}.{existing_version.version_minor}",
            "reused": True,
            "task_id": task.id,
            "feed_url": f"/feed/{feed.id}.xml"
        }

    # Find or create source
    source = (
        db.query(Source)
        .filter(Source.url == url)
        .first()
    )

    if not source:
        parsed = urlparse(url)

        source = Source(
            id=uuid4(),
            name=request.name,
            url=url,
            domain=parsed.netloc
        )

        db.add(source)
        db.flush()

    # Find existing feed for this source
    feed = (
        db.query(Feed)
        .filter(Feed.source_id == source.id)
        .first()
    )

    if not feed:
        feed = Feed(
            id=uuid4(),
            source_id=source.id,
            name=request.name,
            description=request.description,
            refresh_interval_seconds=request.refresh_interval_seconds
        )

        db.add(feed)
        db.flush()

    # Create next version
    latest_version = (
        db.query(FeedVersion)
        .filter(FeedVersion.feed_id == feed.id)
        .order_by(
            FeedVersion.version_major.desc(),
            FeedVersion.version_minor.desc()
        )
        .first()
    )

    if latest_version:
        version_major = latest_version.version_major
        version_minor = latest_version.version_minor + 1
    else:
        version_major = 1
        version_minor = 1

    version = FeedVersion(
        id=uuid4(),
        feed_id=feed.id,
        version_major=version_major,
        version_minor=version_minor,
        config_hash=config_hash,
        config_path="",
        script_path=""
    )

    db.add(version)
    db.flush()

    # Save scraper configuration
    feed_configuration = FeedConfiguration(
        feed_version_id=version.id,
        item_selector=configuration["item_selector"],
        title_selector=configuration.get("title_selector"),
        link_selector=configuration.get("link_selector"),
        date_selector=configuration.get("date_selector"),
        description_selector=configuration.get("description_selector"),
        image_selector=configuration.get("image_selector"),
        author_selector=configuration.get("author_selector"),
        category_selector=configuration.get("category_selector"),
        pagination_selector=configuration.get("pagination_selector"),
        rendering_mode=configuration.get("rendering_mode", "request"),
        max_items=configuration.get("max_items"),
    )

    db.add(feed_configuration)

    feed.current_version_id = version.id
    db.commit()
    db.refresh(version)

    # Generate and save the actual scraper.py
    generate_scraper(db, version.id)

    version.status = "ready"
    feed.status = "ready"

    db.commit()

    # Queue the saved scraper for execution
    task = run_feed_task.delay(str(version.id))

    return {
        "feed_id": str(feed.id),
        "feed_version_id": str(version.id),
        "version": f"v{version_major}.{version_minor}",
        "reused": False,
        "task_id": task.id,
        "feed_url": f"/feed/{feed.id}.xml"
    }
