from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AssessmentResponse(BaseModel):
    id: int
    checkin_id: int
    case_id: int
    risk_level: str
    risk_category: str = "low"
    direction: str
    score: int
    confidence: float | None = None
    reason: str
    model_version: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LongitudinalTrendItem(BaseModel):
    checkin_id: int
    assessment_id: int | None = None
    timestamp: datetime
    score: int
    risk_level: str
    risk_category: str
    direction: str
    reason: str


class CaseTrendsResponse(BaseModel):
    case_id: int
    case_code: str
    total_checkins: int
    current_risk_level: str
    current_risk_category: str
    overall_direction: str
    average_score: float
    history: list[LongitudinalTrendItem]
