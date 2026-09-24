import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from app.models.feed_configuration import FeedConfiguration
from app.models.feed_version import FeedVersion
from app.models.feed import Feed
from app.models.source import Source


BASE_DIR = Path(__file__).resolve().parents[2]

TEMPLATE_DIR = BASE_DIR / "templates"
GENERATED_FEEDS_DIR = BASE_DIR / "generated_feeds"


def generate_scraper(
    db: Session,
    feed_version_id: str
):
    # Find scraper configuration
    configuration = (
        db.query(FeedConfiguration)
        .filter(
            FeedConfiguration.feed_version_id == feed_version_id
        )
        .first()
    )

    if configuration is None:
        raise ValueError("Scraper configuration not found")

    # Find feed version
    version = (
        db.query(FeedVersion)
        .filter(
            FeedVersion.id == feed_version_id
        )
        .first()
    )

    if version is None:
        raise ValueError("Feed version not found")

    # Find feed
    feed = (
        db.query(Feed)
        .filter(
            Feed.id == version.feed_id
        )
        .first()
    )

    if feed is None:
        raise ValueError("Feed not found")

    # Find source
    source = (
        db.query(Source)
        .filter(
            Source.id == feed.source_id
        )
        .first()
    )

    if source is None:
        raise ValueError("Source not found")

    # Create Jinja environment
    environment = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR))
    )

    template = environment.get_template(
        "scraper_template.py.j2"
    )

    # Data passed into the Jinja template
    template_data = {
        "url": source.url,

        "item_selector": configuration.item_selector,
        "title_selector": configuration.title_selector,
        "link_selector": configuration.link_selector,
        "date_selector": configuration.date_selector,
        "description_selector": configuration.description_selector,
        "image_selector": configuration.image_selector,
        "author_selector": configuration.author_selector,
        "category_selector": configuration.category_selector,

        "pagination_selector": configuration.pagination_selector,

        "max_items": configuration.max_items,

        "rendering_mode": (
            configuration.rendering_mode
            or "request"
        ),
    }

    # Generate scraper.py
    generated_code = template.render(
        **template_data
    )

    version_name = (
        f"v{version.version_major}.{version.version_minor}"
    )

    # Create:
    # generated_feeds/<feed_id>/<version>/
    version_directory = (
        GENERATED_FEEDS_DIR
        / str(version.feed_id)
        / version_name
    )

    version_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    scraper_path = (
        version_directory / "scraper.py"
    )

    config_path = (
        version_directory / "config.json"
    )

    # Save generated scraper
    scraper_path.write_text(
        generated_code,
        encoding="utf-8"
    )

    # Save configuration snapshot
    config_data = {
        "feed_version_id": str(version.id),
        "feed_id": str(version.feed_id),
        "version": version_name,

        "source_url": source.url,

        "item_selector": configuration.item_selector,
        "title_selector": configuration.title_selector,
        "link_selector": configuration.link_selector,
        "date_selector": configuration.date_selector,
        "description_selector": configuration.description_selector,
        "image_selector": configuration.image_selector,
        "author_selector": configuration.author_selector,
        "category_selector": configuration.category_selector,

        "pagination_selector": (
             configuration.pagination_selector
             if configuration.pagination_selector
             and configuration.pagination_selector.lower() != "null"
             else None
         ),

        "max_items": configuration.max_items,

        "rendering_mode": (
            configuration.rendering_mode
            or "request"
        ),
    }

    config_path.write_text(
        json.dumps(
            config_data,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    # Persist artifact paths in PostgreSQL
    version.script_path = str(
        scraper_path
    )

    version.config_path = str(
        config_path
    )

    db.commit()
    db.refresh(version)

    return {
        "scraper_path": str(scraper_path),
        "config_path": str(config_path),
        "version": version_name,
    }