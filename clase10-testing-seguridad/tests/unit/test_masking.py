from app.security.masking import enmascarar_telefono


def test_masks_all_but_the_last_four_digits():
    telefono = "+573001234567"

    resultado = enmascarar_telefono(telefono)

    assert resultado == "*** *** 4568"


def test_short_phone_numbers_are_still_masked():
    telefono = "123"

    resultado = enmascarar_telefono(telefono)

    assert resultado == "*** 123"


def test_exactly_four_digits_is_the_boundary_case():
    telefono = "1234"

    resultado = enmascarar_telefono(telefono)

    assert resultado == "*** 1234"
