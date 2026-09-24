from pydantic import BaseModel, HttpUrl


class FeedCreateRequest(BaseModel):
    source_id: str
    name: str
    description: str | None = None
    refresh_interval_seconds: int = 1800


class FeedVersionCreateRequest(BaseModel):
    version_major: int = 1
    version_minor: int = 1


class ScraperConfigurationInput(BaseModel):
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


class BuildFeedRequest(BaseModel):
    url: HttpUrl
    name: str
    description: str | None = None
    refresh_interval_seconds: int = 1800
    configuration: ScraperConfigurationInput


class BuildFeedResponse(BaseModel):
    feed_id: str
    feed_version_id: str
    version: str
    reused: bool
    task_id: str | None = None
    feed_url: str
