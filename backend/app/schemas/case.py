from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CaseCreate(BaseModel):
    case_code: str = Field(
        min_length=3,
        max_length=50,
    )


class CaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_code: str
    status: str
    created_at: datetime
    updated_at: datetime