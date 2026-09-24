from pydantic import BaseModel


class ScraperConfigurationRequest(BaseModel):
    feed_version_id: str
    item_selector: str
    title_selector: str | None = None
    link_selector: str | None = None
    date_selector: str | None = None
    description_selector: str | None = None
    image_selector: str | None = None
    author_selector: str | None = None
    category_selector: str | None = None
    pagination_selector: str | None = None
    rendering_mode: str = "request"
    max_items: int | None = None