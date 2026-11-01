CREATE TABLE grupos (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(trim(name)) BETWEEN 1 AND 30),
    kind TEXT NOT NULL CHECK (kind IN ('projeto', 'area')),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived')),
    created_at TEXT NOT NULL
);

CREATE INDEX idx_grupos_status ON grupos (status);

ALTER TABLE tasks ADD COLUMN grupo_id INTEGER REFERENCES grupos(id) ON DELETE SET NULL;

CREATE INDEX idx_tasks_grupo_id ON tasks (grupo_id);

PRAGMA user_version = 3;
