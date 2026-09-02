"""
Slide 20 — Column Masking. The database-level version of this lives in
app/rls.sql (the `reservas_enmascaradas` VIEW); this is the same rule
expressed as a pure Python function so it can be unit tested in isolation
and reused in code paths that don't go through the view.

Also this module's running example in the TDD walkthrough — see
docs/security-architecture.md "TDD paso a paso".
"""


def enmascarar_telefono(telefono: str) -> str:
    if len(telefono) <= 4:
        return "*** " + telefono
    return "*** *** " + telefono[-4:]
