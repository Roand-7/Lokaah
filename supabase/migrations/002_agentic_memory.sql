-- Migration: Agentic Memory System
-- Enables persistent conversation history, session summaries, and concept mastery tracking
-- For: VEDA teaching agent with memory across sessions

-- ============================================================================
-- CONVERSATION HISTORY
-- ============================================================================

DROP TABLE IF EXISTS conversation_history CASCADE;

CREATE TABLE conversation_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id TEXT NOT NULL,
    user_id TEXT,  -- Optional user identifier
    agent_type TEXT NOT NULL CHECK (agent_type IN ('veda', 'oracle', 'pulse', 'atlas', 'spark', 'supervisor')),
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',  -- Stores concept tags, difficulty, language, etc.
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- SESSION SUMMARIES
-- ============================================================================

DROP TABLE IF EXISTS session_summaries CASCADE;

CREATE TABLE session_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id TEXT NOT NULL UNIQUE,
    user_id TEXT,
    total_messages INTEGER DEFAULT 0,
    concepts_discussed TEXT[] DEFAULT '{}',  -- List of concept identifiers
    primary_agent TEXT,  -- Which agent was used most
    learning_streak INTEGER DEFAULT 0,  -- Consecutive days of learning
    summary TEXT,  -- AI-generated summary of session
    sentiment TEXT CHECK (sentiment IN ('positive', 'neutral', 'frustrated', 'confused')),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_active_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- CONCEPT MASTERY (Bayesian Knowledge Tracing)
-- ============================================================================

DROP TABLE IF EXISTS concept_mastery CASCADE;

CREATE TABLE concept_mastery (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    concept TEXT NOT NULL,  -- e.g., "quadratic_equations", "pythagoras_theorem"
    chapter TEXT,  -- e.g., "Algebra", "Geometry"
    subject TEXT DEFAULT 'mathematics',
    
    -- Bayesian Knowledge Tracing parameters
    p_know FLOAT DEFAULT 0.0 CHECK (p_know >= 0 AND p_know <= 1),  -- Probability student knows concept
    p_learn FLOAT DEFAULT 0.3 CHECK (p_learn >= 0 AND p_learn <= 1),  -- Learning rate
    p_guess FLOAT DEFAULT 0.25 CHECK (p_guess >= 0 AND p_guess <= 1),  -- Probability of guessing correctly
    p_slip FLOAT DEFAULT 0.1 CHECK (p_slip >= 0 AND p_slip <= 1),  -- Probability of making careless mistake
    
    -- Tracking
    total_attempts INTEGER DEFAULT 0,
    correct_attempts INTEGER DEFAULT 0,
    consecutive_correct INTEGER DEFAULT 0,
    last_attempt_correct BOOLEAN,
    mastery_level TEXT DEFAULT 'not_started' CHECK (mastery_level IN ('not_started', 'learning', 'practicing', 'mastered', 'needs_review')),
    
    -- Timestamps
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_practiced_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(user_id, concept)
);

-- ============================================================================
-- CONCEPT ATTEMPTS (Detailed attempt history)
-- ============================================================================

DROP TABLE IF EXISTS concept_attempts CASCADE;

CREATE TABLE concept_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    concept TEXT NOT NULL,
    question_id TEXT,  -- Reference to question if available
    
    -- Attempt details
    is_correct BOOLEAN NOT NULL,
    time_taken_seconds INTEGER,  -- How long to answer
    difficulty FLOAT CHECK (difficulty >= 0 AND difficulty <= 1),
    hint_used BOOLEAN DEFAULT false,
    attempt_number INTEGER DEFAULT 1,  -- Which attempt for this question
    
    -- Answer details
    student_answer TEXT,
    correct_answer TEXT,
    feedback TEXT,  -- AI-generated feedback
    
    -- Context
    source TEXT DEFAULT 'oracle' CHECK (source IN ('oracle', 'photo', 'exam', 'practice')),
    metadata JSONB DEFAULT '{}',
    
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- LEARNING SESSIONS (Track learning sessions)
-- ============================================================================

DROP TABLE IF EXISTS learning_sessions CASCADE;

CREATE TABLE learning_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id TEXT NOT NULL UNIQUE,
    user_id TEXT,
    
    -- Session details
    session_type TEXT CHECK (session_type IN ('study', 'practice', 'exam', 'revision', 'photo_help')),
    subject TEXT,
    chapter TEXT,
    concepts_covered TEXT[] DEFAULT '{}',
    
    -- Metrics
    total_questions INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    time_spent_minutes INTEGER DEFAULT 0,
    engagement_score FLOAT CHECK (engagement_score >= 0 AND engagement_score <= 1),
    
    -- Session state
    is_active BOOLEAN DEFAULT true,
    completed BOOLEAN DEFAULT false,
    
    -- Timestamps
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- STUDENT ATTEMPTS (From ORACLE question generation)
-- ============================================================================

DROP TABLE IF EXISTS student_attempts CASCADE;

CREATE TABLE student_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id TEXT NOT NULL,
    user_id TEXT,
    question_id TEXT NOT NULL,
    
    -- Attempt details
    answer TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    marks_obtained FLOAT,
    marks_total FLOAT,
    time_taken_seconds INTEGER,
    
    -- Question context
    concept TEXT NOT NULL,
    difficulty FLOAT,
    source TEXT DEFAULT 'oracle' CHECK (source IN ('oracle', 'ai', 'pattern', 'photo')),
    
    -- Feedback
    feedback TEXT,
    hints_used INTEGER DEFAULT 0,
    attempt_number INTEGER DEFAULT 1,
    
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- INDEXES for Performance
-- ============================================================================

-- Conversation history indexes
CREATE INDEX IF NOT EXISTS idx_conversation_history_session_id ON conversation_history(session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_history_user_id ON conversation_history(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_history_agent_type ON conversation_history(agent_type);
CREATE INDEX IF NOT EXISTS idx_conversation_history_timestamp ON conversation_history(timestamp DESC);

-- Session summaries indexes
CREATE INDEX IF NOT EXISTS idx_session_summaries_user_id ON session_summaries(user_id);
CREATE INDEX IF NOT EXISTS idx_session_summaries_last_active ON session_summaries(last_active_at DESC);

-- Concept mastery indexes
CREATE INDEX IF NOT EXISTS idx_concept_mastery_user_id ON concept_mastery(user_id);
CREATE INDEX IF NOT EXISTS idx_concept_mastery_concept ON concept_mastery(concept);
CREATE INDEX IF NOT EXISTS idx_concept_mastery_mastery_level ON concept_mastery(mastery_level);
CREATE INDEX IF NOT EXISTS idx_concept_mastery_user_concept ON concept_mastery(user_id, concept);

-- Concept attempts indexes
CREATE INDEX IF NOT EXISTS idx_concept_attempts_user_id ON concept_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_concept_attempts_session_id ON concept_attempts(session_id);
CREATE INDEX IF NOT EXISTS idx_concept_attempts_concept ON concept_attempts(concept);
CREATE INDEX IF NOT EXISTS idx_concept_attempts_attempted_at ON concept_attempts(attempted_at DESC);

-- Learning sessions indexes
CREATE INDEX IF NOT EXISTS idx_learning_sessions_session_id ON learning_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_learning_sessions_user_id ON learning_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_sessions_is_active ON learning_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_learning_sessions_started_at ON learning_sessions(started_at DESC);

-- Student attempts indexes
CREATE INDEX IF NOT EXISTS idx_student_attempts_session_id ON student_attempts(session_id);
CREATE INDEX IF NOT EXISTS idx_student_attempts_user_id ON student_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_student_attempts_question_id ON student_attempts(question_id);
CREATE INDEX IF NOT EXISTS idx_student_attempts_concept ON student_attempts(concept);
CREATE INDEX IF NOT EXISTS idx_student_attempts_attempted_at ON student_attempts(attempted_at DESC);

-- ============================================================================
-- COMMENTS (Documentation)
-- ============================================================================

COMMENT ON TABLE conversation_history IS 'Stores all conversation messages between students and AI agents';
COMMENT ON TABLE session_summaries IS 'Auto-generated summaries of learning sessions (every 10 turns)';
COMMENT ON TABLE concept_mastery IS 'Bayesian Knowledge Tracing for each student-concept pair';
COMMENT ON TABLE concept_attempts IS 'Detailed history of every concept attempt';
COMMENT ON TABLE learning_sessions IS 'Tracks complete learning sessions with metrics';
COMMENT ON TABLE student_attempts IS 'Student answers to ORACLE-generated questions';

COMMENT ON COLUMN concept_mastery.p_know IS 'Probability that student knows the concept (0.0 to 1.0)';
COMMENT ON COLUMN concept_mastery.p_learn IS 'Learning rate - how quickly student picks up concept';
COMMENT ON COLUMN concept_mastery.p_guess IS 'Probability of guessing correct answer without knowledge';
COMMENT ON COLUMN concept_mastery.p_slip IS 'Probability of careless mistake despite knowledge';

-- ============================================================================
-- FUNCTIONS for Auto-Update
-- ============================================================================

-- Update 'updated_at' timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables with updated_at
DROP TRIGGER IF EXISTS update_session_summaries_updated_at ON session_summaries;
CREATE TRIGGER update_session_summaries_updated_at BEFORE UPDATE ON session_summaries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_concept_mastery_updated_at ON concept_mastery;
CREATE TRIGGER update_concept_mastery_updated_at BEFORE UPDATE ON concept_mastery
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_learning_sessions_updated_at ON learning_sessions;
CREATE TRIGGER update_learning_sessions_updated_at BEFORE UPDATE ON learning_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Agentic Memory System migration completed successfully!';
    RAISE NOTICE 'Tables created: conversation_history, session_summaries, concept_mastery, concept_attempts, learning_sessions, student_attempts';
    RAISE NOTICE 'All indexes and triggers configured.';
END $$;
