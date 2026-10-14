
from datetime import datetime

from pydantic import BaseModel, Field


class SafeContactCreate(BaseModel):
    contact_name: str = Field(min_length=1, max_length=150)
    relationship: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=1, max_length=30)
    preferred_language: str | None = Field(default=None, max_length=50)
    preferred_channel: str = Field(min_length=1, max_length=50)
    safe_time: str | None = Field(default=None, max_length=100)
    neutral_notification: bool = True
    fallback_contact: str | None = None


class SafeContactResponse(BaseModel):
    id: int
    case_id: int
    contact_name: str
    relationship: str
    phone: str
    preferred_language: str | None = None
    preferred_channel: str
    safe_time: str | None = None
    neutral_notification: bool
    fallback_contact: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
