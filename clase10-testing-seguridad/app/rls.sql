ALTER TABLE reservas ENABLE ROW LEVEL SECURITY;
ALTER TABLE reservas FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS solo_mi_restaurante ON reservas;
CREATE POLICY solo_mi_restaurante ON reservas
  USING (restaurante_id = NULLIF(current_setting('app.restaurante_id', true), '')::int);

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
