"""Communication API endpoints for SMS and Voice/IVR multi-channel intake."""

import os
from typing import Any
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.security.auth import get_current_user
from app.security.permissions import require_roles
from app.services.case_service import get_case
from app.services.communication_service import (
    process_inbound_ivr_event,
    process_inbound_sms,
    send_wellness_reminder,
)
from integrations.sms.provider import get_sms_provider
from integrations.ivr.provider import get_ivr_provider

router = APIRouter(
    prefix="/communication",
    tags=["Communication"],
)


class InboundSMSRequest(BaseModel):
    sender_phone: str = Field(min_length=5, max_length=30)
    message: str = Field(min_length=1, max_length=2000)
    idempotency_key: str | None = Field(default=None, max_length=128)


class ReminderRequest(BaseModel):
    case_id: int
    phone_number: str = Field(min_length=5, max_length=30)


class DeliveryStatusWebhook(BaseModel):
    message_id: str
    status: str
    error_code: str | None = None


@router.post("/sms/inbound")
def handle_inbound_sms(
    payload: InboundSMSRequest,
    db: Session = Depends(get_db),
):
    """Receive and normalize an inbound SMS message into the check-in assessment pipeline."""
    try:
        result = process_inbound_sms(
            db=db,
            sender_phone=payload.sender_phone,
            sms_text=payload.message,
            idempotency_key=payload.idempotency_key,
        )
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post("/sms/reminder")
def trigger_wellness_reminder(
    payload: ReminderRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Dispatch a privacy-preserving wellness reminder SMS."""
    case = get_case(db=db, case_id=payload.case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    user_role = current_user.get("role", "")
    is_owner = case.user_id == current_user["user_id"]
    is_staff = user_role in ("admin", "caseworker", "counsellor")

    if not (is_owner or is_staff):
        raise HTTPException(status_code=403, detail="You do not have access to this case")

    try:
        res = send_wellness_reminder(
            db=db,
            case_id=payload.case_id,
            phone_number=payload.phone_number,
            requested_by=current_user["user_id"],
        )
        return {
            "status": res.status,
            "message_id": res.message_id,
            "is_mock": res.is_mock,
            "provider": res.provider_name,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/sms/status")
def handle_sms_delivery_status(
    payload: DeliveryStatusWebhook,
):
    """Webhook for SMS telecom delivery receipts."""
    return {
        "received": True,
        "message_id": payload.message_id,
        "status": payload.status,
    }


@router.post("/voice/callback")
async def handle_ivr_callback(
    request: Request,
    x_provider_signature: str | None = Header(None),
    db: Session = Depends(get_db),
):
    """Webhook callback for incoming IVR telephony events (DTMF / voice responses)."""
    raw_body = await request.body()
    try:
        payload = await request.json()
    except Exception:
        # Support urlencoded or empty JSON
        form = await request.form()
        payload = dict(form)

    try:
        result = process_inbound_ivr_event(
            db=db,
            payload=payload,
            raw_body=raw_body,
            signature=x_provider_signature,
        )
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get("/providers/status")
def get_providers_status(
    current_user: dict = Depends(require_roles("admin", "caseworker", "counsellor")),
):
    """Inspect active communication provider integrations and configuration."""
    sms_provider = get_sms_provider()
    ivr_provider = get_ivr_provider()

    return {
        "sms": {
            "provider": sms_provider.__class__.__name__,
            "is_mock": "Mock" in sms_provider.__class__.__name__,
            "gateway_configured": bool(os.getenv("SMS_GATEWAY_URL") and os.getenv("SMS_GATEWAY_KEY")),
        },
        "voice_ivr": {
            "provider": ivr_provider.__class__.__name__,
            "is_mock": "Mock" in ivr_provider.__class__.__name__,
            "webhook_security": bool(os.getenv("IVR_WEBHOOK_SECRET")),
        },
        "supported_channels": ["web", "sms", "ivr"],
    }
