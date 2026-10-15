from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    checkin_id: Mapped[int] = mapped_column(
        ForeignKey("checkins.id"),
        nullable=False,
        index=True,
    )

    case_id: Mapped[int] = mapped_column(
        ForeignKey("victim_cases.id"),
        nullable=False,
        index=True,
    )

    risk_level: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    direction: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    confidence: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    model_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    @property
    def risk_category(self) -> str:
        """Mutually exclusive 4-tier category:
        - Low: 0–3
        - Moderate: greater than 3 and below 7 (scores 4, 5, 6)
        - High: 7 and below 8 (score 7)
        - Urgent: 8–10 (or direct safety escalation rule)
        """
        if self.risk_level == "urgent":
            return "urgent"
        if self.score >= 8:
            return "urgent"
        if 7 <= self.score < 8 or self.risk_level == "high":
            return "high"
        if 3 < self.score < 7 or self.risk_level == "follow_up":
            return "moderate"
        return "low"
