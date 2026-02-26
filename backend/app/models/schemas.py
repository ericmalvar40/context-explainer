from pydantic import BaseModel


class ExplainRequest(BaseModel):
    post_text: str
    post_image_url: str | None = None


class Source(BaseModel):
    title: str
    url: str


class ExplainResponse(BaseModel):
    bullets: list[str]
    sources: list[Source]
    metadata: dict
