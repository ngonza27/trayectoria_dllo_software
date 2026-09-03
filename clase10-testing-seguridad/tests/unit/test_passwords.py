from app.security.passwords import hash_password, verify_password


def test_hash_password_is_not_the_plain_text():
    plain = "Segura123!"

    hashed = hash_password(plain)

    assert hashed != plain
    assert hashed.startswith("$2b$")


def test_hash_password_is_salted_and_therefore_not_deterministic():
    plain = "Segura123!"

    first_hash = hash_password(plain)
    second_hash = hash_password(plain)

    assert first_hash != second_hash


def test_verify_password_accepts_the_correct_password():
    plain = "Segura123!"
    hashed = hash_password(plain)

    result = verify_password(plain, hashed)

    assert result is True


def test_verify_password_rejects_the_wrong_password():
    hashed = hash_password("Segura123!")

    result = verify_password("otra-contraseña", hashed)

    assert result is False
