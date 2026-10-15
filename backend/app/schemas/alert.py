from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AlertResponse(BaseModel):
    id: int
    case_id: int

    alert_type: str
    risk_level: str

    status: str

    reason: str
    direction: str
    confidence: float | None = None
    assigned_to: int | None = None
    action_reason: str | None = None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertAction(BaseModel):
    action: str = Field(
        pattern="^(acknowledge|assign|escalate|resolve|dismiss)$"
    )

    reason: str | None = Field(
        default=None,
        max_length=1000,
    )

    assigned_to: int | None = Field(
        default=None,
        description="ID of the user to assign this alert to",
    )