from app.config import settings
from app.security.jwt import create_access_token


class InvalidClientError(Exception):
    pass


def issue_client_credentials_token(client_id: str, client_secret: str) -> str:
    if client_id != settings.oauth_client_id or client_secret != settings.oauth_client_secret:
        raise InvalidClientError("invalid_client")

    return create_access_token(
        subject=client_id,
        email="",
        rol="service",
        restaurante_id=0,
        extra_claims={"grant_type": "client_credentials", "scope": "reservas:read"},
    )
