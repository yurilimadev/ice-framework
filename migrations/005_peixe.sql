CREATE TABLE leads (
    id INTEGER PRIMARY KEY,
    company TEXT NOT NULL CHECK (length(trim(company)) BETWEEN 1 AND 120),
    contact TEXT,
    sector TEXT NOT NULL CHECK (length(trim(sector)) BETWEEN 1 AND 60),
    city TEXT NOT NULL CHECK (length(trim(city)) BETWEEN 1 AND 60),
    channel TEXT NOT NULL CHECK (channel IN ('whatsapp', 'linkedin', 'email', 'instagram', 'presencial')),
    handle TEXT NOT NULL CHECK (length(trim(handle)) BETWEEN 1 AND 200),
    observation TEXT NOT NULL CHECK (length(trim(observation)) BETWEEN 1 AND 200),
    status TEXT NOT NULL DEFAULT 'novo' CHECK (status IN (
        'novo', 'a_enviar', 'enviado', 'respondeu', 'conversa',
        'proposta', 'piloto', 'ganho', 'perdido', 'pausado'
    )),
    next_action_at TEXT CHECK (next_action_at IS NULL OR length(next_action_at) = 10),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE UNIQUE INDEX idx_leads_channel_handle ON leads (channel, handle);
CREATE INDEX idx_leads_status ON leads (status);
CREATE INDEX idx_leads_next_action ON leads (next_action_at);
CREATE INDEX idx_leads_created_at ON leads (created_at);

CREATE TABLE interactions (
    id INTEGER PRIMARY KEY,
    lead_id INTEGER NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    kind TEXT NOT NULL CHECK (kind IN (
        'mensagem', 'resposta', 'conversa', 'proposta', 'piloto', 'nota', 'pausa'
    )),
    channel TEXT NOT NULL CHECK (channel IN ('whatsapp', 'linkedin', 'email', 'instagram', 'presencial', 'sistema')),
    notes TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX idx_interactions_lead ON interactions (lead_id);
CREATE INDEX idx_interactions_kind_created ON interactions (kind, created_at);
CREATE INDEX idx_interactions_created ON interactions (created_at);

CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT INTO settings (key, value) VALUES
    ('daily_target', '1'),
    ('weekly_messages', '5'),
    ('weekly_replies', '2'),
    ('weekly_conversations', '1'),
    ('current_ocean', 'odontologia'),
    ('current_city', 'Natal');

PRAGMA user_version = 5;
