from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.source import Source


router = APIRouter(
    prefix="/sources",
    tags=["Sources"]
)


@router.post("/")
def create_source(
    name: str,
    url: str,
    db: Session = Depends(get_db)
):
    source = Source(
        id=uuid4(),
        name=name,
        url=url,
        domain=url.split("/")[2] if "://" in url else url
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    return {
        "message": "Source created",
        "source_id": str(source.id)
    }