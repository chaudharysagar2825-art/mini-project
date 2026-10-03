from datetime import datetime

from pydantic import BaseModel, Field


class ReferralCreate(BaseModel):
    referral_type: str = Field(
        pattern="^(mental_health|welfare|protection|legal|financial|rehab)$"
    )

    organization: str = Field(
        min_length=1,
        max_length=200,
    )

    reason: str = Field(
        min_length=1,
        max_length=1000,
    )

    priority: str = Field(
        default="routine",
        pattern="^(routine|follow_up|urgent)$",
    )


class ReferralResponse(BaseModel):
    id: int
    case_id: int

    referral_type: str
    organization: str
    reason: str
    priority: str

    status: str

    created_at: datetime
    updated_at: datetime