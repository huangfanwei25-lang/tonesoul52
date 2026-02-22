-- ToneSoul Supabase Migration
-- Run this in Supabase SQL Editor after creating a project.

-- Table: SoulDB memory events
CREATE TABLE soul_memories (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    source TEXT NOT NULL,
    payload JSONB NOT NULL,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_memories_source ON soul_memories(source);
CREATE INDEX idx_memories_created ON soul_memories(created_at DESC);

-- Table: conversations
CREATE TABLE conversations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Table: messages (cascade delete with conversation)
CREATE TABLE messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    deliberation JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_messages_conv ON messages(conversation_id, created_at);

-- Table: audit logs
CREATE TABLE audit_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    gate_decision TEXT,
    p_level_triggered TEXT,
    poav_score REAL,
    delta_t REAL,
    delta_s REAL,
    delta_sigma REAL,
    delta_r REAL,
    rationale TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_audit_created ON audit_logs(created_at DESC);

-- Table: evolution results (semantic graph / contradiction snapshots / distillation outputs)
CREATE TABLE evolution_results (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    result_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_evolution_results_created ON evolution_results(created_at DESC);
CREATE INDEX idx_evolution_results_type ON evolution_results(result_type);
CREATE INDEX idx_evolution_results_conversation ON evolution_results(conversation_id);

-- Enable Row Level Security (RLS)
ALTER TABLE soul_memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE evolution_results ENABLE ROW LEVEL SECURITY;

-- Allow backend service role full access (Render backend uses service key)
CREATE POLICY "Service role full access" ON soul_memories FOR ALL USING (true);
CREATE POLICY "Service role full access" ON conversations FOR ALL USING (true);
CREATE POLICY "Service role full access" ON messages FOR ALL USING (true);
CREATE POLICY "Service role full access" ON audit_logs FOR ALL USING (true);
CREATE POLICY "Service role full access" ON evolution_results FOR ALL USING (true);
