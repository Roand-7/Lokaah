-- Migration: Photo Solver - Solved Questions Storage
-- Stores all questions solved via photo upload for future reference

CREATE TABLE IF NOT EXISTS solved_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id TEXT NOT NULL,
    image_hash TEXT NOT NULL UNIQUE,  -- SHA-256 hash for deduplication
    subject TEXT NOT NULL CHECK (subject IN ('mathematics', 'physics', 'chemistry', 'biology', 'social_science', 'english')),
    chapter TEXT,
    question_text TEXT NOT NULL,
    solution TEXT NOT NULL,
    explanation TEXT,
    key_concepts TEXT[] DEFAULT '{}',
    difficulty_level FLOAT CHECK (difficulty_level >= 0 AND difficulty_level <= 1),
    language TEXT DEFAULT 'english',
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
    solved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for fast queries
CREATE INDEX idx_solved_questions_session_id ON solved_questions(session_id);
CREATE INDEX idx_solved_questions_subject ON solved_questions(subject);
CREATE INDEX idx_solved_questions_solved_at ON solved_questions(solved_at DESC);
CREATE INDEX idx_solved_questions_image_hash ON solved_questions(image_hash);

-- Comments
COMMENT ON TABLE solved_questions IS 'Stores all questions solved via photo upload for student reference and analytics';
COMMENT ON COLUMN solved_questions.image_hash IS 'SHA-256 hash of image for deduplication';
COMMENT ON COLUMN solved_questions.confidence IS 'AI confidence in solution (0.0 to 1.0)';
COMMENT ON COLUMN solved_questions.difficulty_level IS 'Estimated difficulty (0.0=easy, 1.0=hard)';
