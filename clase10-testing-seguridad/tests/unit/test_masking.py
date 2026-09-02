"""
Slide 20 — Column Masking, plus the running example for the TDD walkthrough
in docs/security-architecture.md ("TDD paso a paso"). If you're doing that
exercise: comment out the body of enmascarar_telefono (RED), make these
pass one at a time with the minimum code (GREEN), then clean up (REFACTOR)
without breaking any of them.
"""

from app.security.masking import enmascarar_telefono


def test_masks_all_but_the_last_four_digits():
    # Arrange
    telefono = "+573001234567"

    # Act
    resultado = enmascarar_telefono(telefono)

    # Assert
    assert resultado == "*** *** 4567"


def test_short_phone_numbers_are_still_masked():
    # Arrange
    telefono = "123"

    # Act
    resultado = enmascarar_telefono(telefono)

    # Assert — too short for the "last 4" rule to make sense, but never shown raw
    assert resultado == "*** 123"


def test_exactly_four_digits_is_the_boundary_case():
    # Arrange
    telefono = "1234"

    # Act
    resultado = enmascarar_telefono(telefono)

    # Assert
    assert resultado == "*** 1234"
