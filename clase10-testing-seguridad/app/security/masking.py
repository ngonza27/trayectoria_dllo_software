"""
Slide 20 — Column Masking. The database-level version of this lives in
app/rls.sql (the `cuentas_enmascaradas` VIEW); this is the same rule
expressed as a pure Python function so it can be unit tested in isolation
and reused in code paths that don't go through the view.

Also this module's running example in the TDD walkthrough — see
docs/security-architecture.md "TDD paso a paso".
"""


def enmascarar_numero_cuenta(numero_cuenta: str) -> str:
    if len(numero_cuenta) <= 4:
        return "**** " + numero_cuenta
    return "**** **** **** " + numero_cuenta[-4:]
