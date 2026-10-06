from pydantic import BaseModel, HttpUrl


class WebsiteRequest(BaseModel):
    url: HttpUrl
    rendering_mode: str = "request"