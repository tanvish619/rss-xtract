from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.configuration_schema import ScraperConfigurationRequest
from app.models.feed_configuration import FeedConfiguration


router = APIRouter(
    prefix="/configurations",
    tags=["Configurations"]
)


@router.post("/")
def create_configuration(
    request: ScraperConfigurationRequest,
    db: Session = Depends(get_db)
):
    configuration = FeedConfiguration(
        feed_version_id=request.feed_version_id,
        item_selector=request.item_selector,
        title_selector=request.title_selector,
        link_selector=request.link_selector,
        date_selector=request.date_selector,
        description_selector=request.description_selector,
        image_selector=request.image_selector,
        author_selector=request.author_selector,
        category_selector=request.category_selector,
        pagination_selector=request.pagination_selector,
        rendering_mode=request.rendering_mode,
        max_items=request.max_items,
    )

    db.add(configuration)
    db.commit()
    db.refresh(configuration)

    return {
        "message": "Scraper configuration saved",
        "configuration_id": str(configuration.id)
    }