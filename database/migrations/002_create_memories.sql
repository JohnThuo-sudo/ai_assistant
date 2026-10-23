
-- Migration 002: Create approved long-term memory storage.

CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    content TEXT NOT NULL
        CHECK (length(trim(content)) > 0),

    source_conversation_id UUID
        REFERENCES conversations(id)
        ON DELETE SET NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    expires_at TIMESTAMPTZ,

    CHECK (
        expires_at IS NULL
        OR expires_at > created_at
    )
);

-- Supports efficient lookup of memories that have an expiry date.
CREATE INDEX idx_memories_expires_at
    ON memories (expires_at)
    WHERE expires_at IS NOT NULL;
