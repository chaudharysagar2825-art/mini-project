from datetime import datetime

from pydantic import BaseModel, Field


class ConsentCreate(BaseModel):
    status: str = Field(
        pattern="^(granted|paused|withdrawn)$"
    )
    version: str = Field(min_length=1, max_length=50)
    scope: str = Field(min_length=1, max_length=1000)
    channel: str = Field(min_length=1, max_length=50)


class ConsentResponse(BaseModel):
    id: int
    case_id: int
    status: str
    version: str
    scope: str
    channel: str

    consented_at: datetime | None = None
    paused_at: datetime | None = None
    withdrawn_at: datetime | None = None

    created_at: datetime