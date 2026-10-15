from datetime import datetime
from pydantic import BaseModel, Field, field_validator


REFERRAL_TYPE_ALIASES = {
    "medical": "rehab",
    "psychological_counselling": "mental_health",
    "counselling": "mental_health",
    "shelter": "welfare",
    "legal_aid": "legal",
    "financial_aid": "financial",
    "protection_services": "protection",
}


class ReferralCreate(BaseModel):
    referral_type: str = Field(
        pattern="^(mental_health|welfare|protection|legal|financial|rehab)$"
    )
    organization: str = Field(min_length=1, max_length=200)
    reason: str = Field(min_length=1, max_length=1000)
    priority: str = Field(
        default="routine",
        pattern="^(routine|follow_up|urgent)$",
    )

    @field_validator("referral_type", mode="before")
    @classmethod
    def normalize_referral_type(cls, v: str) -> str:
        if isinstance(v, str):
            normalized = v.strip().lower()
            return REFERRAL_TYPE_ALIASES.get(normalized, normalized)
        return v


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

    model_config = {"from_attributes": True}


class ReferralStatusUpdate(BaseModel):
    status: str = Field(
        pattern="^(created|acknowledged|in_progress|completed|cancelled)$"
    )
    notes: str | None = Field(
        default=None,
        max_length=1000,
        description="Follow-up notes or action justification",
    )