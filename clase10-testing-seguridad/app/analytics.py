import logging

import httpx

from app.config import settings

logger = logging.getLogger("analytics")

_client = None
if settings.posthog_project_api_key:
    import posthog

    posthog.api_key = settings.posthog_project_api_key
    posthog.host = settings.posthog_host
    _client = posthog


def capture(event: str, distinct_id: str, properties: dict | None = None) -> None:
    """
    Slide 8/11 — PostHog: instrument 2-3 key MVP events (here: registro,
    login, crear_reserva) so there is real usage evidence for the project
    defense, beyond "the tests pass". No-ops safely when
    POSTHOG_PROJECT_API_KEY is unset, so the app and its test suite never
    depend on a live PostHog project.
    """
    if _client is None:
        logger.info("posthog(no-op): event=%s distinct_id=%s properties=%s", event, distinct_id, properties)
        return
    _client.capture(distinct_id=distinct_id, event=event, properties=properties or {})


def fetch_recent_session_recordings(limit: int = 10) -> list[dict]:
    """
    Read-only PostHog Session Recordings API, used only server-side (see
    app/routers/admin.py) with the *personal* API key — never the project
    key, and never called from the browser. This is how you verify, from
    the terminal or the /admin/analytics/session-recordings endpoint, that a
    replay of one of the two intentional bugs (GUIA-DE-PRUEBAS.md) was
    actually captured, without having to click through the PostHog UI.

    Raises if POSTHOG_PERSONAL_API_KEY is unset — this is a manual
    verification tool, not something the automated test suite depends on
    (it needs a live PostHog project with real recorded sessions).
    """
    if not settings.posthog_personal_api_key:
        raise RuntimeError("POSTHOG_PERSONAL_API_KEY is not set — see .env.example")

    response = httpx.get(
        f"{settings.posthog_host}/api/projects/@current/session_recordings/",
        headers={"Authorization": f"Bearer {settings.posthog_personal_api_key}"},
        params={"limit": limit},
        timeout=10,
    )
    response.raise_for_status()
    return response.json().get("results", [])
