from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, Field


class ShortenRequest(BaseModel):
    url: AnyHttpUrl
    code: str | None = Field(default=None, min_length=1, max_length=64)


class ShortenResponse(BaseModel):
    code: str
    short_url: str
    target_url: str


class LinkInfo(BaseModel):
    code: str
    target_url: str
    clicks: int
    created_at: datetime
