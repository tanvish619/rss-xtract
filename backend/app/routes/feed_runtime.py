from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from fastapi.responses import FileResponse, Response
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.dependencies import get_db

from app.models.feed import Feed
from app.models.feed_version import FeedVersion
from app.models.article import Article

from app.celery_app import celery_app


router = APIRouter(
    tags=["Feed Runtime"]
)


@router.get("/feeds")
def list_feeds(
    db: Session = Depends(get_db),
):

    feeds = (
        db.query(Feed)
        .order_by(
            Feed.created_at.desc()
        )
        .all()
    )

    results = []

    for feed in feeds:

        versions = (
            db.query(FeedVersion)
            .filter(
                FeedVersion.feed_id
                == feed.id
            )
            .order_by(
                FeedVersion.version_major.desc(),
                FeedVersion.version_minor.desc(),
            )
            .all()
        )

        current_version = (
            versions[0]
            if versions
            else None
        )

        article_count = (
            db.query(func.count(Article.id))
            .filter(
                Article.feed_id == feed.id
            )
            .scalar()
            or 0
        )

        results.append({
            "id": str(feed.id),
            "source_id": str(feed.source_id),
            "name": feed.name,
            "description": feed.description,
            "status": feed.status,
            "refresh_interval_seconds": (
                feed.refresh_interval_seconds
            ),
            "current_version": (
                (
                    f"v"
                    f"{current_version.version_major}."
                    f"{current_version.version_minor}"
                )
                if current_version
                else None
            ),
            "created_at": (
                feed.created_at
            ),
            "updated_at": (
                feed.updated_at
            ),
            "last_run_at": (
                feed.last_run_at
            ),
            "last_success_at": (
                feed.last_success_at
            ),
            "last_error": (
                feed.last_error
            ),
            "article_count": article_count,
            "source_url": "",
        })

    return results


@router.get("/feeds/{feed_id}")
def get_feed(
    feed_id: str,
    db: Session = Depends(get_db),
):

    feed = (
        db.query(Feed)
        .filter(Feed.id == feed_id)
        .first()
    )

    if feed is None:
        raise HTTPException(
            status_code=404,
            detail="Feed not found",
        )

    versions = (
        db.query(FeedVersion)
        .filter(
            FeedVersion.feed_id == feed.id
        )
        .order_by(
            FeedVersion.version_major.desc(),
            FeedVersion.version_minor.desc(),
        )
        .all()
    )

    current_version = (
        versions[0]
        if versions
        else None
    )

    article_count = (
        db.query(func.count(Article.id))
        .filter(
            Article.feed_id == feed.id
        )
        .scalar()
        or 0
    )

    return {
        "id": str(feed.id),
        "source_id": str(feed.source_id),
        "name": feed.name,
        "description": feed.description,
        "status": feed.status,
        "refresh_interval_seconds": (
            feed.refresh_interval_seconds
        ),
        "last_run_at": (
            feed.last_run_at
        ),
        "last_success_at": (
            feed.last_success_at
        ),
        "last_error": (
            feed.last_error
        ),
        "current_version": (
            (
                f"v"
                f"{current_version.version_major}."
                f"{current_version.version_minor}"
            )
            if current_version
            else None
        ),
        "article_count": article_count,
        "source_url": "",
        "versions": [
            {
                "id": str(version.id),
                "version": (
                    f"v"
                    f"{version.version_major}."
                    f"{version.version_minor}"
                ),
                "status": version.status,
                "execution_count": (
                    version.execution_count
                ),
                "last_execution_at": (
                    version.last_execution_at
                ),
                "last_success_at": (
                    version.last_success_at
                ),
                "last_error": (
                    version.last_error
                ),
            }
            for version in versions
        ],
        "feed_url": (
            f"/feed/{feed.id}.xml"
        ),
    }


@router.post("/feeds/{feed_id}/run")
def run_feed(
    feed_id: str,
    db: Session = Depends(get_db),
):

    feed = (
        db.query(Feed)
        .filter(Feed.id == feed_id)
        .first()
    )

    if feed is None:
        raise HTTPException(
            status_code=404,
            detail="Feed not found",
        )

    version = (
        db.query(FeedVersion)
        .filter(
            FeedVersion.feed_id == feed.id
        )
        .order_by(
            FeedVersion.version_major.desc(),
            FeedVersion.version_minor.desc(),
        )
        .first()
    )

    if version is None:
        raise HTTPException(
            status_code=404,
            detail="No feed version found",
        )

    task = celery_app.send_task(
        "rss_xtract.run_feed",
        args=[
            str(version.id)
        ],
    )

    return {
        "message": "Feed run queued",
        "feed_id": str(feed.id),
        "feed_version_id": str(
            version.id
        ),
        "task_id": task.id,
    }


@router.get("/feed/rss.xsl")
def get_rss_xsl():
    """Serve the XSLT stylesheet used to render RSS feeds in browsers."""
    xsl_path = (
        Path(__file__)
        .resolve()
        .parents[2]
        / "static"
        / "rss.xsl"
    )

    if not xsl_path.exists():
        raise HTTPException(
            status_code=404,
            detail="XSL stylesheet not found",
        )

    return FileResponse(
        xsl_path,
        media_type="application/xslt+xml",
        headers={"Cache-Control": "public, max-age=3600"},
    )


@router.get(
    "/feed/{feed_id}.xml"
)
def get_feed_xml(
    feed_id: str,
    db: Session = Depends(get_db),
):

    feed = (
        db.query(Feed)
        .filter(Feed.id == feed_id)
        .first()
    )

    if feed is None:
        raise HTTPException(
            status_code=404,
            detail="Feed not found",
        )

    generated_root = (
        Path(__file__)
        .resolve()
        .parents[2]
        / "generated_feeds"
        / str(feed.id)
    )

    latest_path = (
        generated_root
        / "latest.xml"
    )

    if not latest_path.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                "Feed has not completed "
                "a successful run yet."
            ),
        )

    # Read the XML and inject the XSL stylesheet PI so browsers
    # render it beautifully instead of showing raw XML.
    xml_content = latest_path.read_text(encoding="utf-8")

    xsl_pi = (
        '<?xml-stylesheet type="text/xsl" href="/feed/rss.xsl"?>'
    )

    # Insert PI after the XML declaration (first line)
    if xml_content.startswith("<?xml"):
        first_newline = xml_content.index("?>")
        insert_at = first_newline + 2  # after "?>"
        xml_content = (
            xml_content[:insert_at]
            + "\n"
            + xsl_pi
            + xml_content[insert_at:]
        )
    else:
        xml_content = xsl_pi + "\n" + xml_content

    return Response(
        content=xml_content,
        media_type="application/rss+xml",
        headers={"Cache-Control": "no-cache"},
    )
