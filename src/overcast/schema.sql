CREATE TABLE topics (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL CHECK (length(trim(name)) > 0),
  name_key TEXT NOT NULL UNIQUE CHECK (length(trim(name_key)) > 0),
  prompt TEXT NOT NULL CHECK (length(trim(prompt)) > 0),
  language TEXT NOT NULL CHECK (language GLOB '[a-z][a-z]'),
  target_duration_minutes INTEGER NOT NULL CHECK (target_duration_minutes BETWEEN 1 AND 120),
  format TEXT NOT NULL CHECK (format IN ('monologue', 'dialogue')),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
) STRICT;
