import json
import time
from datetime import datetime
from pathlib import Path

from app.celery_app import celery_app

from app.database import SessionLocal
from app.models.feed import Feed
from app.models.feed_version import FeedVersion
from app.models.feed_configuration import FeedConfiguration
from app.models.feed_run import FeedRun
from app.models.article import Article
from app.models.source import Source

from app.services.scraper_executor import execute_scraper
from app.services.article_normalizer import normalize_articles
from app.services.rss_builder import build_rss


@celery_app.task(
    bind=True,
    name="rss_xtract.run_feed",
)
def run_feed_task(
    self,
    feed_version_id: str,
):
    db = SessionLocal()

    started_at = datetime.utcnow()
    start_time = time.perf_counter()

    version = None
    feed = None
    run = None

    try:
        version = (
            db.query(FeedVersion)
            .filter(
                FeedVersion.id == feed_version_id
            )
            .first()
        )

        if version is None:
            raise ValueError(
                "Feed version not found"
            )

        feed = (
            db.query(Feed)
            .filter(
                Feed.id == version.feed_id
            )
            .first()
        )

        if feed is None:
            raise ValueError(
                "Feed not found"
            )

        configuration = (
            db.query(FeedConfiguration)
            .filter(
                FeedConfiguration.feed_version_id
                == version.id
            )
            .first()
        )

        if configuration is None:
            raise ValueError(
                "Feed configuration not found"
            )

        source = (
            db.query(Source)
            .filter(
                Source.id == feed.source_id
            )
            .first()
        )

        if source is None:
            raise ValueError(
                "Source not found"
            )

        run = FeedRun(
            feed_version_id=version.id,
            started_at=started_at,
            status="running",
        )

        db.add(run)

        version.status = "running"
        version.last_execution_at = started_at

        feed.status = "running"
        feed.last_run_at = started_at
        feed.last_error = None

        db.commit()
        db.refresh(run)

        raw_articles = execute_scraper(
            db,
            str(version.id),
        )

        normalized_articles = normalize_articles(
            raw_articles,
            source.url,
        )

        scraper_path = Path(
            version.script_path
        )

        version_directory = scraper_path.parent

        version_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        articles_path = (
            version_directory
            / "articles.json"
        )

        articles_path.write_text(
            json.dumps(
                normalized_articles,
                indent=2,
                ensure_ascii=False,
                default=str,
            ),
            encoding="utf-8",
        )

        seen_guids = set()

        for article_data in normalized_articles:
            guid = article_data["guid"]
            
            if guid in seen_guids:
                continue
            
            seen_guids.add(guid)

            existing = (
                db.query(Article)
                .filter(
                    Article.feed_id == feed.id,
                    Article.guid == guid,
                )
                .first()
            )

            if existing:

                existing.title = (
                    article_data["title"]
                )

                existing.link = (
                    article_data["link"]
                )

                existing.description = (
                    article_data["description"]
                )

                existing.content = (
                    article_data["content"]
                )

                existing.image_url = (
                    article_data["image_url"]
                )

                existing.author = (
                    article_data["author"]
                )

                existing.category = (
                    article_data["category"]
                )

                existing.published_at = (
                    article_data["published_at"]
                )

                existing.last_seen_at = (
                    datetime.utcnow()
                )

            else:

                article = Article(
                    feed_id=feed.id,
                    guid=guid,
                    title=article_data["title"],
                    link=article_data["link"],
                    description=article_data[
                        "description"
                    ],
                    content=article_data[
                        "content"
                    ],
                    image_url=article_data[
                        "image_url"
                    ],
                    author=article_data[
                        "author"
                    ],
                    category=article_data[
                        "category"
                    ],
                    published_at=article_data[
                        "published_at"
                    ],
                )

                db.add(article)

        db.flush()

        feed_url = (
            f"/feed/{feed.id}.xml"
        )

        rss_xml = build_rss(
            feed_title=feed.name,
            feed_description=(
                feed.description
                or f"RSS feed for {source.url}"
            ),
            feed_url=feed_url,
            articles=normalized_articles,
        )

        output_path = (
            version_directory
            / "output.xml"
        )

        output_path.write_text(
            rss_xml,
            encoding="utf-8",
        )

        latest_path = (
            version_directory.parent
            / "latest.xml"
        )

        temporary_latest = (
            version_directory.parent
            / "latest.xml.tmp"
        )

        temporary_latest.write_text(
            rss_xml,
            encoding="utf-8",
        )

        temporary_latest.replace(
            latest_path
        )

        duration_ms = int(
            (
                time.perf_counter()
                - start_time
            )
            * 1000
        )

        log_path = (
            version_directory
            / "run.log"
        )

        log_path.write_text(
            (
                "Status: success\n"
                f"Articles: {len(normalized_articles)}\n"
                f"Duration: {duration_ms} ms\n"
                f"Started: {started_at.isoformat()}\n"
                f"Finished: {datetime.utcnow().isoformat()}\n"
            ),
            encoding="utf-8",
        )

        run.status = "success"
        run.finished_at = datetime.utcnow()
        run.article_count = (
            len(normalized_articles)
        )
        run.duration_ms = duration_ms
        run.log_path = str(log_path)

        version.status = "success"
        version.execution_count += 1
        version.last_success_at = (
            datetime.utcnow()
        )
        version.last_error = None

        feed.status = "success"
        feed.last_success_at = (
            datetime.utcnow()
        )
        feed.last_error = None

        db.commit()

        return {
            "status": "success",
            "feed_id": str(feed.id),
            "feed_version_id": str(
                version.id
            ),
            "article_count": len(
                normalized_articles
            ),
            "duration_ms": duration_ms,
        }

    except Exception as exc:

        error_message = str(exc)

        duration_ms = int(
            (
                time.perf_counter()
                - start_time
            )
            * 1000
        )

        if version is not None:
            version.status = "failed"
            version.last_error = error_message

        if feed is not None:
            feed.status = "failed"
            feed.last_error = error_message

        if run is not None:
            run.status = "failed"
            run.finished_at = datetime.utcnow()
            run.duration_ms = duration_ms
            run.error_message = error_message

        if version is not None:

            try:

                log_path = (
                    Path(version.script_path).parent
                    / "run.log"
                )

                log_path.write_text(
                    (
                        "Status: failed\n"
                        f"Error: {error_message}\n"
                        f"Duration: {duration_ms} ms\n"
                    ),
                    encoding="utf-8",
                )

                if run is not None:
                    run.log_path = str(
                        log_path
                    )

            except Exception:
                pass

        db.commit()

        raise

    finally:
        db.close()
