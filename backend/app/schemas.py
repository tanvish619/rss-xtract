from pydantic import BaseModel, HttpUrl


class WebsiteRequest(BaseModel):
    url: HttpUrl