from app.database import SessionLocal
from app.models.source import Source
from app.models.feed import Feed
from app.models.feed_version import FeedVersion
from app.models.feed_configuration import FeedConfiguration

from app.services.scraper_generator import generate_scraper

from uuid import uuid4


db = SessionLocal()

try:

    # Create test source
    source = Source(
        id=uuid4(),
        name="Local Pagination Test",
        url="http://127.0.0.1:9000/",
        domain="127.0.0.1:9000"
    )

    db.add(source)
    db.flush()

    # Create test feed
    feed = Feed(
        id=uuid4(),
        source_id=source.id,
        name="Pagination Test Feed"
    )

    db.add(feed)
    db.flush()

    # Create test version
    version = FeedVersion(
        id=uuid4(),
        feed_id=feed.id,
        version_major=1,
        version_minor=1,
        config_hash="pagination-test",
        config_path="",
        script_path=""
    )

    db.add(version)
    db.flush()

    # Create scraper configuration
    configuration = FeedConfiguration(
        id=uuid4(),
        feed_version_id=version.id,

        item_selector="article",
        title_selector="h2",
        link_selector="a",
        description_selector="p",

        pagination_selector="a.next-page",

        rendering_mode="js"
    )

    db.add(configuration)
    db.commit()

    # Generate actual scraper.py
    result = generate_scraper(
        db=db,
        feed_version_id=str(version.id)
    )

    print("Pagination test scraper generated!")
    print(f"Feed ID: {feed.id}")
    print(f"Version ID: {version.id}")
    print(f"Scraper: {result['scraper_path']}")

finally:
    db.close()