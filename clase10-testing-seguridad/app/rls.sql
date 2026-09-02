-- Run once against the target database after the tables exist (see README.md).
-- This file is the literal SQL from Semana_10 slides 22 and 23, applied to the
-- `reservas` table created by SQLAlchemy's Base.metadata.create_all().

-- ---------------------------------------------------------------------------
-- Slide 22 — Row-Level Security
-- ---------------------------------------------------------------------------
ALTER TABLE reservas ENABLE ROW LEVEL SECURITY;

-- By default Postgres does NOT apply RLS policies to a table's owner — and
-- since the application's own role (reservas_app) is what creates this table
-- via SQLAlchemy, it owns it. FORCE makes the policy apply to the owner too.
-- (Superusers still always bypass RLS, no matter what: that's why
-- docker-compose.yml and tests/integration/conftest.py both go out of their
-- way to make reservas_app NOSUPERUSER — see "El superusuario invisible" in
-- docs/security-architecture.md.)
ALTER TABLE reservas FORCE ROW LEVEL SECURITY;

-- current_setting('app.restaurante_id', true) returns NULL when the GUC was
-- never set in this session at all, but once any transaction has done a
-- SET LOCAL app.restaurante_id, Postgres keeps a placeholder for the rest of
-- the session and its value reverts to '' (empty string, not NULL) once that
-- transaction ends — casting '' straight to ::int raises invalid_text_
-- representation. NULLIF(..., '') normalizes both "never set" and "set,
-- then reverted" to NULL, so the comparison below just evaluates to
-- NULL (no match) instead of erroring.
DROP POLICY IF EXISTS solo_mi_restaurante ON reservas;
CREATE POLICY solo_mi_restaurante ON reservas
  USING (restaurante_id = NULLIF(current_setting('app.restaurante_id', true), '')::int);

-- Without WITH CHECK, Postgres reuses USING for INSERT/UPDATE too, so a
-- connection cannot insert or move a row into a restaurant it does not
-- belong to, either — not just read one.

-- ---------------------------------------------------------------------------
-- Slide 23 — Column Masking via a VIEW
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW reservas_enmascaradas AS
SELECT
  id,
  restaurante_id,
  cliente_nombre,
  '*** *** ' || RIGHT(telefono, 4) AS telefono,
  fecha_hora,
  num_personas,
  mesa_numero,
  estado,
  created_at
FROM reservas;

-- Postgres applies RLS on the underlying `reservas` table even when queried
-- through this view (the view has no elevated privileges of its own), so a
-- non-gerente user reading `reservas_enmascaradas` still only sees their own
-- restaurant's rows, now with the guest's phone number masked.
