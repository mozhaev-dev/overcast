CREATE TABLE topics (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL CHECK (length(trim(name)) > 0),
  prompt TEXT NOT NULL CHECK (length(trim(prompt)) > 0),
  language TEXT NOT NULL,
  target_duration_minutes INTEGER NOT NULL CHECK (target_duration_minutes > 0),
  format TEXT NOT NULL CHECK (format IN ('monologue', 'dialogue')),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
) STRICT;
