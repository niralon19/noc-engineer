CREATE TABLE IF NOT EXISTS noc_memory (
 memory_id UUID PRIMARY KEY,
 memory_type TEXT NOT NULL CHECK (memory_type IN ('incident','service_context','runbook_reference','topology_reference','lesson_learned')),
 subject TEXT NOT NULL,
 content JSONB NOT NULL,
 source_ref TEXT NOT NULL,
 confidence NUMERIC(4,3),
 observed_at TIMESTAMPTZ NOT NULL,
 expires_at TIMESTAMPTZ,
 created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_noc_memory_subject ON noc_memory(subject);
CREATE INDEX IF NOT EXISTS idx_noc_memory_type_time ON noc_memory(memory_type, observed_at DESC);
