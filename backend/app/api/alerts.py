from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.alert import AlertAction, AlertResponse
from app.security.auth import get_current_user
from app.services.alert_service import (
    get_alert,
    get_case_alerts,
    update_alert_status,
)
from app.services.case_service import get_case


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
)


@router.get(
    "/{alert_id}",
    response_model=AlertResponse,
)
def get_alert_by_id(
    alert_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    alert = get_alert(
        db=db,
        alert_id=alert_id,
    )

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail="Alert not found",
        )

    case = get_case(
        db=db,
        case_id=alert.case_id,
    )

    if case is None or case.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this alert",
        )

    return alert


@router.get(
    "/case/{case_id}",
    response_model=list[AlertResponse],
)
def get_alerts_for_case(
    case_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    case = get_case(
        db=db,
        case_id=case_id,
    )

    if case is None:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    if case.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this case",
        )

    return get_case_alerts(
        db=db,
        case_id=case_id,
    )


@router.patch(
    "/{alert_id}/action",
    response_model=AlertResponse,
)
def action_alert(
    alert_id: int,
    data: AlertAction,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    alert = get_alert(
        db=db,
        alert_id=alert_id,
    )

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail="Alert not found",
        )

    case = get_case(
        db=db,
        case_id=alert.case_id,
    )

    if case is None or case.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this alert",
        )

    try:
        return update_alert_status(
            db=db,
            alert_id=alert_id,
            action=data.action,
            reason=data.reason,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )