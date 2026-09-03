def enmascarar_telefono(telefono: str) -> str:
    if len(telefono) <= 4:
        return "*** " + telefono
    return "*** *** " + telefono[-4:]
