"""
Slide 6 — Unit tests, Arrange-Act-Assert (AAA). Each test below is one unit
of business logic, isolated from the database and the HTTP layer, so it runs
in milliseconds — this whole file should finish in well under a second.
"""

from app.security.passwords import hash_password, verify_password


def test_hash_password_is_not_the_plain_text():
    # Arrange
    plain = "Segura123!"

    # Act
    hashed = hash_password(plain)

    # Assert
    assert hashed != plain
    assert hashed.startswith("$2b$")  # bcrypt hash prefix


def test_hash_password_is_salted_and_therefore_not_deterministic():
    # Arrange
    plain = "Segura123!"

    # Act
    first_hash = hash_password(plain)
    second_hash = hash_password(plain)

    # Assert — same input, different hash, because bcrypt salts each call
    assert first_hash != second_hash


def test_verify_password_accepts_the_correct_password():
    # Arrange
    plain = "Segura123!"
    hashed = hash_password(plain)

    # Act
    result = verify_password(plain, hashed)

    # Assert
    assert result is True


def test_verify_password_rejects_the_wrong_password():
    # Arrange
    hashed = hash_password("Segura123!")

    # Act
    result = verify_password("otra-contraseña", hashed)

    # Assert
    assert result is False
