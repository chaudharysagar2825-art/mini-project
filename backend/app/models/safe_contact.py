from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SafeContact(Base):
    __tablename__ = "safe_contacts"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    case_id: Mapped[int] = mapped_column(
        ForeignKey("victim_cases.id"),
        nullable=False,
        index=True,
    )

    contact_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    relationship: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    phone: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    preferred_language: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
    )

    preferred_channel: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    safe_time: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    neutral_notification: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    fallback_contact: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )