from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CheckIn(Base):
    __tablename__ = "checkins"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    case_id: Mapped[int] = mapped_column(
        ForeignKey("victim_cases.id"),
        nullable=False,
        index=True,
    )

    questionnaire_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    answers: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    direct_safety_concern: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    user_skipped_questions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    requested_human_contact: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="submitted",
        nullable=False,
    )

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )