import logging

from app.config import settings

logger = logging.getLogger("analytics")

_client = None
if settings.posthog_project_api_key:
    import posthog

    posthog.api_key = settings.posthog_project_api_key
    posthog.host = settings.posthog_host
    _client = posthog


def capture(event: str, distinct_id: str, properties: dict | None = None) -> None:
    if _client is None:
        logger.info("posthog(no-op): event=%s distinct_id=%s properties=%s", event, distinct_id, properties)
        return
    _client.capture(distinct_id=distinct_id, event=event, properties=properties or {})


