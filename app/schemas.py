from pydantic import BaseModel
from datetime import datetime

class URLBase(BaseModel):
    original_url: str

class URLCreate(URLBase):
    pass

class URLInfo(URLBase):
    id: int
    short_code: str
    created_at: datetime
    short_url: str  # 👈 Add this field

    class Config:
        orm_mode = True

