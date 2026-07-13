-- 0001 — baseline schema for the lab's screens.
-- Applied by scripts/migrate.sh (golang-migrate); the applied position is
-- tracked in the schema_migrations table of the target database.
CREATE TABLE production_kpi (
    id BIGSERIAL PRIMARY KEY,
    line TEXT NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    units_produced INT NOT NULL,
    units_rejected INT NOT NULL DEFAULT 0
);

-- A few rows so a SELECT on a fresh database shows something.
INSERT INTO production_kpi (line, units_produced, units_rejected) VALUES
    ('packaging-1', 1180, 12),
    ('packaging-2', 1075, 4),
    ('filling-1', 2210, 31);
