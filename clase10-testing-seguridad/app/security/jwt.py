import time
from functools import lru_cache

import jwt
from jwt import PyJWKClient

from app.config import settings


class InvalidTokenError(Exception):
    pass


def create_access_token(
    *, subject: str, email: str, rol: str, organizacion_id: int, extra_claims: dict | None = None
) -> str:
    """
    Slide 13 — JWT structure: header (algorithm) + payload (claims) + signature.
    This is this app's own "identity provider" for local development
    (AUTH_PROVIDER=local). It issues the same claim shape Cognito/Azure AD
    would (sub, email, exp, iss, aud, plus our custom `rol`/`organizacion_id`)
    so the rest of the app never has to know which provider issued the token.
    """
    now = int(time.time())
    payload = {
        "sub": subject,
        "email": email,
        "rol": rol,
        "organizacion_id": organizacion_id,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": now,
        "exp": now + settings.jwt_expire_minutes * 60,
    }
    if extra_claims:
        payload.update(extra_claims)
    # Never put secrets (passwords, card numbers) in the payload: it is
    # base64, not encrypted — anyone can decode it without the key.
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


@lru_cache
def _jwks_client(jwks_url: str) -> PyJWKClient:
    return PyJWKClient(jwks_url)


def _cognito_issuer() -> str:
    return f"https://cognito-idp.{settings.cognito_region}.amazonaws.com/{settings.cognito_user_pool_id}"


def _azure_issuer() -> str:
    return f"https://login.microsoftonline.com/{settings.azure_tenant_id}/v2.0"


def decode_and_validate_token(token: str) -> dict:
    """
    Slide 13/14 — "Validar, no solo decodificar": verify the signature against
    the issuer's public key, then check exp/iss/aud, before trusting anything
    in the payload. Which issuer we validate against is controlled by
    AUTH_PROVIDER, so protected routes work unchanged against:
      - AUTH_PROVIDER=local   (this app's own /auth/login, HS256 shared secret)
      - AUTH_PROVIDER=cognito (a real AWS Cognito User Pool, RS256 + JWKS)
      - AUTH_PROVIDER=azure   (a real Azure AD / Entra ID tenant, RS256 + JWKS)
    Only "local" is exercised by the test suite in this repo — cognito/azure
    require a real tenant, see docs/security-architecture.md.
    """
    try:
        if settings.auth_provider == "cognito":
            jwks_url = f"{_cognito_issuer()}/.well-known/jwks.json"
            signing_key = _jwks_client(jwks_url).get_signing_key_from_jwt(token)
            # Cognito ACCESS tokens carry `client_id`, not `aud` — verify that
            # claim manually after decoding if you only accept your own app.
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
