from pydantic import BaseModel, HttpUrl

class URLCreate(BaseModel):
    url: HttpUrl

class URLInfo(BaseModel):
    short_url: str