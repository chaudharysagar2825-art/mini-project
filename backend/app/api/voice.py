from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.security.auth import get_current_user
from app.services.voice_service import analyze_voice


router = APIRouter(
    prefix="/voice",
    tags=["Voice"],
)


class VoiceRequest(BaseModel):
    text: str


@router.post("/analyze")
def analyze_voice_input(
    data: VoiceRequest,
    current_user: dict = Depends(get_current_user),
):
    try:
        result = analyze_voice(data.text)

        return {
            "user_id": current_user["user_id"],
            "result": result,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )