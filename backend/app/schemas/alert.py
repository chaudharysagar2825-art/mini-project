from datetime import datetime

from pydantic import BaseModel, Field


class AlertResponse(BaseModel):
    id: int
    case_id: int

    alert_type: str
    risk_level: str

    status: str

    reason: str
    direction: str
    confidence: float | None = None

    created_at: datetime


class AlertAction(BaseModel):
    action: str = Field(
        pattern="^(acknowledge|assign|escalate|resolve|dismiss)$"
    )

    reason: str | None = Field(
        default=None,
        max_length=1000,
    )