from datetime import datetime

from pydantic import BaseModel, Field


class CheckInAnswer(BaseModel):
    question_id: str = Field(min_length=1, max_length=100)
    answer: str = Field(min_length=1, max_length=2000)


class CheckInCreate(BaseModel):
    questionnaire_version: str = Field(
        min_length=1,
        max_length=50,
    )

    answers: list[CheckInAnswer] = Field(
        min_length=1,
        max_length=50,
    )

    direct_safety_concern: bool | None = None

    user_skipped_questions: list[str] = Field(
        default_factory=list,
        max_length=50,
    )

    requested_human_contact: bool = False


class CheckInResponse(BaseModel):
    id: int
    case_id: int
    questionnaire_version: str

    status: str
    submitted_at: datetime

    risk_level: str | None = None