CREATE TABLE IF NOT EXISTS advisory_reports (
    id SERIAL PRIMARY KEY,
    client_name TEXT NOT NULL,
    cargo_json TEXT NOT NULL,
    advisory_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
