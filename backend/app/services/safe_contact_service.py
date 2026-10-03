from sqlalchemy.orm import Session

from app.models.safe_contact import SafeContact
from app.models.victim_case import VictimCase


def create_safe_contact(
    db: Session,
    case_id: int,
    contact_name: str,
    relationship: str,
    phone: str,
    preferred_language: str | None,
    preferred_channel: str,
    safe_time: str | None,
    neutral_notification: bool,
    fallback_contact: str | None,
) -> SafeContact:

    case = db.get(VictimCase, case_id)

    if case is None:
        raise ValueError("Case not found")

    contact = SafeContact(
        case_id=case_id,
        contact_name=contact_name,
        relationship=relationship,
        phone=phone,
        preferred_language=preferred_language,
        preferred_channel=preferred_channel,
        safe_time=safe_time,
        neutral_notification=neutral_notification,
        fallback_contact=fallback_contact,
        is_active=True,
    )

    db.add(contact)
    db.commit()
    db.refresh(contact)

    return contact


def get_safe_contact(
    db: Session,
    contact_id: int,
) -> SafeContact | None:

    return db.get(SafeContact, contact_id)


def get_case_safe_contacts(
    db: Session,
    case_id: int,
) -> list[SafeContact]:

    return (
        db.query(SafeContact)
        .filter(
            SafeContact.case_id == case_id,
            SafeContact.is_active.is_(True),
        )
        .order_by(SafeContact.created_at.desc())
        .all()
    )


def deactivate_safe_contact(
    db: Session,
    contact_id: int,
) -> SafeContact:

    contact = db.get(SafeContact, contact_id)

    if contact is None:
        raise ValueError("Safe contact not found")

    contact.is_active = False

    db.commit()
    db.refresh(contact)

    return contact