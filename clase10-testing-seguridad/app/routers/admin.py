from fastapi import APIRouter, Depends, HTTPException, status

from app.analytics import fetch_recent_session_recordings
from app.deps import require_role

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/analytics/session-recordings")
def session_recordings(claims: dict = Depends(require_role("gerente"))):
    """
    Manual verification helper for slide 8/11 (PostHog): lists the most
    recent session replays using the read-only PERSONAL API key
    (POSTHOG_PERSONAL_API_KEY), so you can confirm — from this API instead of
    clicking through the PostHog UI — that a replay of one of the two
    intentional bugs (GUIA-DE-PRUEBAS.md) was actually recorded. gerente-only
    because it exposes recording metadata, and it needs a live PostHog
    project with real traffic, so it is NOT covered by the automated test
    suite (tests never depend on a live third-party service).
    """
    try:
        return {"recordings": fetch_recent_session_recordings()}
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
