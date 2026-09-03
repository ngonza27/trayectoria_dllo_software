import time

import pytest

from app.security.jwt import InvalidTokenError, create_access_token, decode_and_validate_token


def test_a_freshly_issued_token_is_valid():
    token = create_access_token(subject="1", email="demo@puy.com", rol="mesero", restaurante_id=1)

    claims = decode_and_validate_token(token)

    assert claims["sub"] == "1"
    assert claims["email"] == "demo@puy.com"
    assert claims["rol"] == "mesero"
    assert claims["restaurante_id"] == 1


def test_payload_is_base64_not_encrypted_anyone_can_read_it_without_the_key():
    token = create_access_token(subject="1", email="demo@puy.com", rol="mesero", restaurante_id=1)
    header_b64, payload_b64, _signature = token.split(".")

    import base64
    import json

    padded = payload_b64 + "=" * (-len(payload_b64) % 4)
    payload = json.loads(base64.urlsafe_b64decode(padded))

    assert payload["email"] == "demo@puy.com"


def test_expired_token_is_rejected():
    now = int(time.time())
    token = create_access_token(
        subject="1",
        email="demo@puy.com",
        rol="mesero",
        restaurante_id=1,
        extra_claims={"iat": now - 3600, "exp": now - 1},
    )

    with pytest.raises(InvalidTokenError):
        decode_and_validate_token(token)


def test_tampered_signature_is_rejected():
    token = create_access_token(subject="1", email="demo@puy.com", rol="mesero", restaurante_id=1)
    header, payload, signature = token.split(".")
    flipped_char = "A" if signature[-1] != "A" else "B"
    tampered_token = f"{header}.{payload}.{signature[:-1]}{flipped_char}"

    with pytest.raises(InvalidTokenError):
        decode_and_validate_token(tampered_token)


def test_wrong_issuer_is_rejected():
    token = create_access_token(
        subject="1",
        email="demo@puy.com",
        rol="mesero",
        restaurante_id=1,
        extra_claims={"iss": "un-emisor-no-confiable"},
    )

    with pytest.raises(InvalidTokenError):
        decode_and_validate_token(token)


def test_wrong_audience_is_rejected():
    token = create_access_token(
        subject="1",
        email="demo@puy.com",
        rol="mesero",
        restaurante_id=1,
        extra_claims={"aud": "otra-api"},
    )

    with pytest.raises(InvalidTokenError):
        decode_and_validate_token(token)
