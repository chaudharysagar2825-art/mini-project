from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    user_id: int | None,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    details: str | None = None,
    ip_address: str | None = None,
) -> AuditLog:

    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log


def get_audit_logs(
    db: Session,
    user_id: int | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
) -> list[AuditLog]:

    query = db.query(AuditLog)

    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)

    if resource_type is not None:
        query = query.filter(
            AuditLog.resource_type == resource_type
        )

    if resource_id is not None:
        query = query.filter(
            AuditLog.resource_id == resource_id
        )

    return (
        query
        .order_by(AuditLog.created_at.desc())
        .all()
    )