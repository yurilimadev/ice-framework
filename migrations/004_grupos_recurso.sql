PRAGMA foreign_keys = OFF;

CREATE TABLE grupos_novo (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(trim(name)) BETWEEN 1 AND 30),
    kind TEXT NOT NULL CHECK (kind IN ('projeto', 'area', 'recurso')),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived')),
    created_at TEXT NOT NULL
);

INSERT INTO grupos_novo (id, name, kind, status, created_at)
SELECT id, name, kind, status, created_at FROM grupos;

DROP TABLE grupos;

ALTER TABLE grupos_novo RENAME TO grupos;

CREATE INDEX idx_grupos_status ON grupos (status);

PRAGMA foreign_keys = ON;

PRAGMA user_version = 4;
