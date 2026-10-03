CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL CHECK (length(trim(title)) BETWEEN 1 AND 120),
    impact INTEGER NOT NULL CHECK (impact BETWEEN 1 AND 10),
    confidence INTEGER NOT NULL CHECK (confidence BETWEEN 1 AND 10),
    ease INTEGER NOT NULL CHECK (ease BETWEEN 1 AND 10),
    deadline TEXT CHECK (deadline IS NULL OR length(deadline) = 10),
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'completed')),
    created_at TEXT NOT NULL
);

CREATE INDEX idx_tasks_status ON tasks (status);
CREATE INDEX idx_tasks_deadline ON tasks (deadline);
CREATE INDEX idx_tasks_created_at ON tasks (created_at);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (length(trim(name)) BETWEEN 1 AND 30)
);

CREATE TABLE task_tags (
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);

CREATE INDEX idx_task_tags_tag_id ON task_tags (tag_id);

PRAGMA user_version = 2;
