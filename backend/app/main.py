from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.voice import router as voice_router
from app.api.cases import router as cases_router
from app.api.consent import router as consent_router
from app.api.checkins import router as checkins_router
from app.api.alerts import router as alerts_router
from app.api.referrals import router as referrals_router
from app.api.audit import router as audit_router
from app.api.dashboards import router as dashboards_router


app = FastAPI(
    title="Manas Setu API",
    description="Backend API for the Manas Setu project",
    version="0.1.0",
)


app.include_router(auth_router)
app.include_router(cases_router)
app.include_router(consent_router)
app.include_router(checkins_router)
app.include_router(alerts_router)
app.include_router(referrals_router)
app.include_router(audit_router)
app.include_router(dashboards_router)
app.include_router(voice_router)


@app.get("/")
def root():
    return {
        "message": "Manas Setu backend is running"
    }