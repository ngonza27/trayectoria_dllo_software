-- Runs once, automatically, the first time the `db` container's data volume
-- is created (official Postgres image behavior for docker-entrypoint-initdb.d),
-- as the bootstrap superuser (POSTGRES_USER, default "postgres").
--
-- The application must NEVER connect as that bootstrap superuser: Postgres
-- unconditionally exempts superusers from Row-Level Security (slide 22), so
-- the RLS policy in app/rls.sql would silently do nothing. This creates a
-- second, deliberately unprivileged role for the app to use instead.

CREATE ROLE reservas_app WITH LOGIN PASSWORD 'reservas_app' NOSUPERUSER NOBYPASSRLS;
CREATE DATABASE reservas_db OWNER reservas_app;
