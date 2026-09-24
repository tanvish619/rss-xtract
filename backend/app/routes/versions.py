from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.feed_schema import FeedVersionCreateRequest
from app.models.feed_version import FeedVersion


router = APIRouter(
    prefix="/feeds",
    tags=["Feed Versions"]
)


@router.post("/{feed_id}/versions")
def create_feed_version(
    feed_id: str,
    request: FeedVersionCreateRequest,
    db: Session = Depends(get_db)
):
    version = FeedVersion(
        id=uuid4(),
        feed_id=feed_id,
        version_major=request.version_major,
        version_minor=request.version_minor,
        config_hash="pending",
        config_path="",
        script_path=""
    )

    db.add(version)
    db.commit()
    db.refresh(version)

    return {
        "message": "Feed version created",
        "feed_version_id": str(version.id),
        "version": f"v{version.version_major}.{version.version_minor}"
    }