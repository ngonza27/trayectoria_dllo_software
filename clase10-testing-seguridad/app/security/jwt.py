import time
from functools import lru_cache

import jwt
from jwt import PyJWKClient

from app.config import settings


class InvalidTokenError(Exception):
    pass


def create_access_token(
    *, subject: str, email: str, rol: str, restaurante_id: int, extra_claims: dict | None = None
) -> str:
    now = int(time.time())
    payload = {
        "sub": subject,
        "email": email,
        "rol": rol,
        "restaurante_id": restaurante_id,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": now,
        "exp": now + settings.jwt_expire_minutes * 60,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


@lru_cache
def _jwks_client(jwks_url: str) -> PyJWKClient:
    return PyJWKClient(jwks_url)


def _cognito_issuer() -> str:
    return f"https://cognito-idp.{settings.cognito_region}.amazonaws.com/{settings.cognito_user_pool_id}"


def _azure_issuer() -> str:
    return f"https://login.microsoftonline.com/{settings.azure_tenant_id}/v2.0"


def decode_and_validate_token(token: str) -> dict:
    try:
        if settings.auth_provider == "cognito":
            jwks_url = f"{_cognito_issuer()}/.well-known/jwks.json"
            signing_key = _jwks_client(jwks_url).get_signing_key_from_jwt(token)
            return jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=_cognito_issuer(),
                options={"verify_aud": False},
            )
        if settings.auth_provider == "azure":
            jwks_url = f"{_azure_issuer()}/discovery/v2.0/keys"
            signing_key = _jwks_client(jwks_url).get_signing_key_from_jwt(token)
            return jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=_azure_issuer(),
                audience=settings.azure_client_id,
            )
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
    except jwt.PyJWTError as exc:
        raise InvalidTokenError(str(exc)) from exc
