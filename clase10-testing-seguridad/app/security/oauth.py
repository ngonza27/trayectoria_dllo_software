from app.config import settings
from app.security.jwt import create_access_token


class InvalidClientError(Exception):
    pass


def issue_client_credentials_token(client_id: str, client_secret: str) -> str:
    """
    Slide 18 — OAuth 2.0 Client Credentials grant: service-to-service auth,
    no human user in the loop (e.g. a nightly reporting job calling this API).
    Compare with the Authorization-Code-style flow in app/routers/auth.py's
    /auth/login, used when a person is the one signing in.
    """
    if client_id != settings.oauth_client_id or client_secret != settings.oauth_client_secret:
        raise InvalidClientError("invalid_client")

    return create_access_token(
        subject=client_id,
        email="",
        rol="service",
        organizacion_id=0,
        extra_claims={"grant_type": "client_credentials", "scope": "cuentas:read"},
    )
