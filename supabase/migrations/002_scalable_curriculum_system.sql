-- LOKAAH Scalable Curriculum System
-- Supports: Multi-board, Multi-subject, Multi-class, Multi-language
-- Purpose: Scale from CBSE Class 10 Math → All India education

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- CURRICULUM HIERARCHY
-- ============================================================================

-- Boards (CBSE, Karnataka, Kerala, etc.)
CREATE TABLE boards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT UNIQUE NOT NULL,  -- "CBSE", "KARNATAKA", "KERALA"
    name TEXT NOT NULL,
    full_name TEXT,  -- "Central Board of Secondary Education"
    country TEXT DEFAULT 'India',
    default_language TEXT DEFAULT 'en',  -- ISO 639-1 code
    is_active BOOLEAN DEFAULT true,
    logo_url TEXT,
    website_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Subjects (Math, Science, Social Studies, etc.)
CREATE TABLE subjects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT UNIQUE NOT NULL,  -- "MATH", "SCIENCE", "SOCIAL"
    name TEXT NOT NULL,
    icon TEXT,  -- "🧮", "🔬", "🌍"
    color TEXT,  -- "#3b82f6" for UI theming
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Curricula (Board + Subject + Class combination)
CREATE TABLE curricula (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    board_id UUID NOT NULL REFERENCES boards(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    class_level INTEGER NOT NULL CHECK (class_level BETWEEN 1 AND 12),
    academic_year TEXT,  -- "2024-25"
    syllabus_version TEXT,  -- "1.0", "2.0" (track revisions)

    -- Exam structure
    exam_pattern JSONB,  -- Stores sections, question types, marks
    total_marks INTEGER,
    passing_marks INTEGER,
    time_limit_minutes INTEGER,

    -- Metadata
    ncert_aligned BOOLEAN DEFAULT true,
    difficulty_avg FLOAT DEFAULT 0.5 CHECK (difficulty_avg BETWEEN 0 AND 1),
    is_published BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(board_id, subject_id, class_level, academic_year)
);

-- Topics/Chapters (hierarchical structure)
CREATE TABLE topics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    curriculum_id UUID NOT NULL REFERENCES curricula(id) ON DELETE CASCADE,
    code TEXT NOT NULL,  -- "QUADRATIC_EQUATIONS"
    name TEXT NOT NULL,  -- "Quadratic Equations"

    -- Multi-language display names
    display_names JSONB,  -- {"en": "Quadratic Equations", "hi": "द्विघात समीकरण"}

    -- Hierarchy
    parent_topic_id UUID REFERENCES topics(id) ON DELETE CASCADE,
    sequence_order INTEGER DEFAULT 0,
    depth_level INTEGER DEFAULT 0,  -- 0 = chapter, 1 = section, 2 = subsection

    -- Exam weightage
    weightage_marks INTEGER,  -- How many marks in exam

    -- NCERT reference
    ncert_chapter_number INTEGER,
    ncert_page_start INTEGER,
    ncert_page_end INTEGER,

    -- Difficulty
    difficulty_avg FLOAT DEFAULT 0.5 CHECK (difficulty_avg BETWEEN 0 AND 1),

    -- Metadata
    description TEXT,
    learning_objectives TEXT[],
    prerequisites TEXT[],  -- Topic codes that should be learned first
    icon TEXT,
    color TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- QUESTION PATTERNS (REUSABLE TEMPLATES)
-- ============================================================================

CREATE TABLE question_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pattern_id TEXT UNIQUE NOT NULL,  -- "quadratic_discriminant_v1"
    topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,

    -- Pattern metadata
    name TEXT NOT NULL,
    description TEXT,
    difficulty FLOAT DEFAULT 0.5 CHECK (difficulty BETWEEN 0 AND 1),
    marks INTEGER NOT NULL CHECK (marks > 0),
    question_type TEXT,  -- "MCQ", "VSA", "SA", "LA", "CASE_BASED"

    -- Templates (supports multi-language via translations table)
    template_text TEXT NOT NULL,  -- "Find discriminant of {a}x² + {b}x + {c} = 0"

    -- Variable schema
    variables_schema JSONB NOT NULL,  -- {"a": {"min": 1, "max": 5}, "b": {...}}

    -- Solution
    solution_template JSONB NOT NULL,  -- Step-by-step template
    answer_template TEXT NOT NULL,  -- "D = {discriminant}"
    validation_rules JSONB,  -- Python expressions for validation

    -- CBSE marking scheme
    marking_scheme JSONB,  -- {"step1": 1, "step2": 2, "final": 1}
    partial_marks_rules JSONB,
    common_mistakes JSONB,  -- For generating MCQ distractors

    -- Visualization
    visual_type TEXT,  -- "jsxgraph_parabola", "static_diagram", null
    visual_config JSONB,  -- Configuration for visual generator

    -- Quality control
    is_approved BOOLEAN DEFAULT false,
    is_featured BOOLEAN DEFAULT false,
    usage_count INTEGER DEFAULT 0,
    avg_solve_time_seconds INTEGER,
    avg_accuracy FLOAT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID,  -- Admin/teacher who created
    approved_by UUID,
    approved_at TIMESTAMPTZ
);

-- ============================================================================
-- MULTILINGUAL SUPPORT (VERNACULAR EXPANSION)
-- ============================================================================

CREATE TABLE translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type TEXT NOT NULL,  -- "pattern", "topic", "hint", "subject", "board"
    entity_id UUID NOT NULL,
    language_code TEXT NOT NULL,  -- ISO 639-1: "hi", "ta", "te", "kn", "ml", "bn", "mr"
    field_name TEXT NOT NULL,  -- "template_text", "name", "description", "hint"
    content JSONB NOT NULL,  -- Stores translated content

    -- Translation quality
    translation_source TEXT DEFAULT 'ai',  -- "ai", "human", "verified"
    quality_score FLOAT,  -- 0-1 (human verified = 1.0)

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    translated_by UUID,  -- User ID if human translated

    UNIQUE(entity_type, entity_id, language_code, field_name)
);

-- ============================================================================
-- STUDENT PROGRESS (MULTI-CURRICULUM)
-- ============================================================================

-- Student's enrollment in curricula
CREATE TABLE student_curriculum_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    curriculum_id UUID NOT NULL REFERENCES curricula(id) ON DELETE CASCADE,

    -- Progress tracking
    enrolled_at TIMESTAMPTZ DEFAULT NOW(),
    current_topic_id UUID REFERENCES topics(id),
    topics_started INTEGER DEFAULT 0,
    topics_mastered INTEGER DEFAULT 0,
    topics_total INTEGER,

    -- Mastery metrics
    overall_mastery FLOAT DEFAULT 0.0 CHECK (overall_mastery BETWEEN 0 AND 1),
    exam_readiness FLOAT DEFAULT 0.0 CHECK (exam_readiness BETWEEN 0 AND 1),
    predicted_score INTEGER,  -- ML-predicted exam score

    -- Engagement
    total_practice_time_minutes INTEGER DEFAULT 0,
    questions_solved INTEGER DEFAULT 0,
    questions_correct INTEGER DEFAULT 0,
    last_practiced TIMESTAMPTZ,

    -- Streaks
    current_streak_days INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_streak_date DATE,

    -- Status
    is_active BOOLEAN DEFAULT true,
    completed_at TIMESTAMPTZ,

    UNIQUE(user_id, curriculum_id)
);

-- Topic-level mastery (granular tracking)
CREATE TABLE topic_mastery (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,

    -- Mastery score (adaptive, based on recent performance)
    mastery_score FLOAT DEFAULT 0.5 CHECK (mastery_score BETWEEN 0 AND 1),

    -- Performance metrics
    questions_solved INTEGER DEFAULT 0,
    questions_correct INTEGER DEFAULT 0,
    total_attempts INTEGER DEFAULT 0,

    -- Time tracking
    total_time_spent_seconds INTEGER DEFAULT 0,
    avg_solve_time_seconds INTEGER,

    -- Analysis
    weak_areas TEXT[],  -- Sub-concepts within topic
    strong_areas TEXT[],
    recommended_practice_count INTEGER DEFAULT 5,

    -- Timestamps
    first_attempt TIMESTAMPTZ,
    last_attempt TIMESTAMPTZ,
    mastered_at TIMESTAMPTZ,  -- When mastery_score reached 0.85+

    UNIQUE(user_id, topic_id)
);

-- ============================================================================
-- GAMIFICATION (ENGAGEMENT SYSTEM)
-- ============================================================================

-- Student XP and levels
CREATE TABLE student_gamification (
    user_id UUID PRIMARY KEY,

    -- XP and levels
    total_xp INTEGER DEFAULT 0,
    current_level INTEGER DEFAULT 1,
    xp_for_next_level INTEGER DEFAULT 100,

    -- Streaks
    current_streak_days INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_practice_date DATE,
    streak_freeze_count INTEGER DEFAULT 0,  -- Duolingo-style streak protection

    -- Curriculum progress
    curricula_enrolled INTEGER DEFAULT 0,
    curricula_completed INTEGER DEFAULT 0,
    chapters_completed INTEGER DEFAULT 0,
    questions_solved_total INTEGER DEFAULT 0,

    -- Accuracy
    overall_accuracy FLOAT DEFAULT 0.0,

    -- Social
    friends_count INTEGER DEFAULT 0,
    study_groups_count INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Achievement badges
CREATE TABLE achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT UNIQUE NOT NULL,  -- "streak_7", "algebra_master", "speed_demon"
    name TEXT NOT NULL,
    description TEXT,
    icon TEXT,  -- "🔥", "🧮", "⚡"
    category TEXT,  -- "streak", "skill", "speed", "social"

    -- Unlock conditions
    condition_type TEXT,  -- "streak_days", "topic_mastery", "speed_record", "xp_total"
    condition_value INTEGER,

    -- Rewards
    xp_reward INTEGER DEFAULT 0,
    badge_rarity TEXT DEFAULT 'common',  -- "common", "rare", "epic", "legendary"

    -- Metadata
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User achievements (unlocked badges)
CREATE TABLE user_achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    achievement_id UUID NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,

    -- Unlock details
    unlocked_at TIMESTAMPTZ DEFAULT NOW(),
    progress_at_unlock JSONB,  -- Snapshot of user stats when unlocked

    -- Display
    is_showcased BOOLEAN DEFAULT false,  -- Show on profile
    showcase_order INTEGER,

    UNIQUE(user_id, achievement_id)
);

-- Leaderboards (weekly/monthly/all-time)
CREATE TABLE leaderboard_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    curriculum_id UUID REFERENCES curricula(id),  -- null = global leaderboard

    -- Leaderboard type
    leaderboard_type TEXT NOT NULL,  -- "weekly", "monthly", "all_time"
    period_start DATE,
    period_end DATE,

    -- Metrics
    xp_earned INTEGER DEFAULT 0,
    questions_solved INTEGER DEFAULT 0,
    rank INTEGER,
    percentile FLOAT,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id, curriculum_id, leaderboard_type, period_start)
);

-- ============================================================================
-- EXAM SIMULATION (MOCK TESTS)
-- ============================================================================

CREATE TABLE mock_tests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    curriculum_id UUID NOT NULL REFERENCES curricula(id) ON DELETE CASCADE,

    -- Test metadata
    name TEXT NOT NULL,
    description TEXT,
    test_type TEXT,  -- "full_mock", "chapter_test", "previous_year"

    -- Structure (matches board exam pattern)
    total_marks INTEGER NOT NULL,
    time_limit_minutes INTEGER NOT NULL,
    sections JSONB NOT NULL,  -- Array of sections with question IDs

    -- Difficulty
    difficulty_level TEXT DEFAULT 'medium',  -- "easy", "medium", "hard"

    -- Source
    source TEXT,  -- "2024_board_paper", "generated", "teacher_created"
    source_year INTEGER,

    -- Metadata
    is_published BOOLEAN DEFAULT false,
    usage_count INTEGER DEFAULT 0,
    avg_score FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID
);

-- Student mock test attempts
CREATE TABLE mock_test_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    mock_test_id UUID NOT NULL REFERENCES mock_tests(id) ON DELETE CASCADE,

    -- Attempt details
    started_at TIMESTAMPTZ DEFAULT NOW(),
    submitted_at TIMESTAMPTZ,
    time_taken_minutes INTEGER,

    -- Scoring
    total_score FLOAT DEFAULT 0,
    max_score INTEGER,
    percentage FLOAT,

    -- Section-wise scores
    section_scores JSONB,  -- {"A": 18, "B": 8, "C": 25, "D": 9}

    -- Answer sheet
    answers JSONB,  -- Array of {question_id, student_answer, is_correct, marks_awarded}

    -- Analysis
    strong_topics TEXT[],
    weak_topics TEXT[],
    time_management_score FLOAT,  -- How well time was managed

    -- Status
    is_completed BOOLEAN DEFAULT false,

    UNIQUE(user_id, mock_test_id, started_at)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Curricula lookups
CREATE INDEX idx_curricula_board_subject_class ON curricula(board_id, subject_id, class_level);
CREATE INDEX idx_curricula_published ON curricula(is_published) WHERE is_published = true;

-- Topics hierarchy and lookups
CREATE INDEX idx_topics_curriculum ON topics(curriculum_id, sequence_order);
CREATE INDEX idx_topics_parent ON topics(parent_topic_id) WHERE parent_topic_id IS NOT NULL;
CREATE INDEX idx_topics_code ON topics(code);

-- Patterns (heavily queried)
CREATE INDEX idx_patterns_topic_difficulty ON question_patterns(topic_id, difficulty, is_approved);
CREATE INDEX idx_patterns_type_marks ON question_patterns(question_type, marks);
CREATE INDEX idx_patterns_approved ON question_patterns(is_approved) WHERE is_approved = true;

-- Translations (fast language switching)
CREATE INDEX idx_translations_entity_lang ON translations(entity_type, entity_id, language_code);

-- Student progress (dashboard queries)
CREATE INDEX idx_progress_user_curriculum ON student_curriculum_progress(user_id, curriculum_id);
CREATE INDEX idx_progress_active ON student_curriculum_progress(user_id, is_active) WHERE is_active = true;
CREATE INDEX idx_mastery_user_topic ON topic_mastery(user_id, topic_id);
CREATE INDEX idx_mastery_weak ON topic_mastery(user_id, mastery_score) WHERE mastery_score < 0.6;

-- Gamification (leaderboards)
CREATE INDEX idx_gamification_xp ON student_gamification(total_xp DESC);
CREATE INDEX idx_leaderboard_period ON leaderboard_entries(leaderboard_type, period_start, rank);

-- Mock tests
CREATE INDEX idx_mock_attempts_user ON mock_test_attempts(user_id, submitted_at DESC);

-- ============================================================================
-- SEED DATA (CBSE CLASS 10 MATHEMATICS)
-- ============================================================================

-- Insert CBSE board
INSERT INTO boards (code, name, full_name, country, default_language) VALUES
('CBSE', 'CBSE', 'Central Board of Secondary Education', 'India', 'en');

-- Insert Mathematics subject
INSERT INTO subjects (code, name, icon, color) VALUES
('MATH', 'Mathematics', '🧮', '#3b82f6');

-- Insert CBSE Class 10 Mathematics curriculum
INSERT INTO curricula (
    board_id,
    subject_id,
    class_level,
    academic_year,
    syllabus_version,
    exam_pattern,
    total_marks,
    passing_marks,
    time_limit_minutes,
    ncert_aligned,
    is_published
) VALUES (
    (SELECT id FROM boards WHERE code = 'CBSE'),
    (SELECT id FROM subjects WHERE code = 'MATH'),
    10,
    '2024-25',
    '1.0',
    '{
        "sections": [
            {"name": "A", "type": "MCQ", "questions": 20, "marks_each": 1, "description": "Multiple Choice Questions"},
            {"name": "B", "type": "VSA", "questions": 5, "marks_each": 2, "description": "Very Short Answer"},
            {"name": "C", "type": "SA", "questions": 6, "marks_each": 3, "description": "Short Answer"},
            {"name": "D", "type": "LA", "questions": 2, "marks_each": 5, "description": "Long Answer"}
        ],
        "time_limit_minutes": 180,
        "internal_choice": true
    }'::jsonb,
    80,
    33,
    180,
    true,
    true
);

-- ============================================================================
-- AUDIT LOGGING (COMPLIANCE & SECURITY)
-- ============================================================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    event_type TEXT NOT NULL,  -- "pattern_created", "translation_added", "student_progress_updated"
    entity_type TEXT,  -- "pattern", "topic", "progress"
    entity_id UUID,
    metadata JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_user_time ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) - MULTI-TENANCY
-- ============================================================================

-- Enable RLS on sensitive tables
ALTER TABLE student_curriculum_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE topic_mastery ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_gamification ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE mock_test_attempts ENABLE ROW LEVEL SECURITY;

-- Students can only see their own data
CREATE POLICY student_own_progress ON student_curriculum_progress
    FOR ALL USING (user_id = auth.uid());

CREATE POLICY student_own_mastery ON topic_mastery
    FOR ALL USING (user_id = auth.uid());

CREATE POLICY student_own_gamification ON student_gamification
    FOR ALL USING (user_id = auth.uid());

-- Public read for boards, subjects, curricula, topics, patterns
ALTER TABLE boards ENABLE ROW LEVEL SECURITY;
ALTER TABLE subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE curricula ENABLE ROW LEVEL SECURITY;
ALTER TABLE topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE question_patterns ENABLE ROW LEVEL SECURITY;

CREATE POLICY public_boards ON boards FOR SELECT USING (is_active = true);
CREATE POLICY public_subjects ON subjects FOR SELECT USING (is_active = true);
CREATE POLICY public_curricula ON curricula FOR SELECT USING (is_published = true);
CREATE POLICY public_topics ON topics FOR SELECT USING (is_active = true);
CREATE POLICY public_patterns ON question_patterns FOR SELECT USING (is_approved = true);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Update mastery score based on recent performance
CREATE OR REPLACE FUNCTION update_topic_mastery(
    p_user_id UUID,
    p_topic_id UUID,
    p_is_correct BOOLEAN
) RETURNS VOID AS $$
BEGIN
    INSERT INTO topic_mastery (user_id, topic_id, mastery_score, questions_solved, questions_correct, last_attempt)
    VALUES (
        p_user_id,
        p_topic_id,
        CASE WHEN p_is_correct THEN 0.65 ELSE 0.35 END,
        1,
        CASE WHEN p_is_correct THEN 1 ELSE 0 END,
        NOW()
    )
    ON CONFLICT (user_id, topic_id)
    DO UPDATE SET
        questions_solved = topic_mastery.questions_solved + 1,
        questions_correct = topic_mastery.questions_correct + CASE WHEN p_is_correct THEN 1 ELSE 0 END,
        mastery_score = LEAST(1.0, GREATEST(0.0,
            topic_mastery.mastery_score + CASE
                WHEN p_is_correct THEN 0.10
                ELSE -0.05
            END
        )),
        last_attempt = NOW();
END;
$$ LANGUAGE plpgsql;

-- Calculate exam readiness (weighted average of topic mastery)
CREATE OR REPLACE FUNCTION calculate_exam_readiness(p_user_id UUID, p_curriculum_id UUID)
RETURNS FLOAT AS $$
DECLARE
    v_readiness FLOAT;
BEGIN
    SELECT
        COALESCE(
            SUM(tm.mastery_score * t.weightage_marks) / NULLIF(SUM(t.weightage_marks), 0),
            0.0
        ) INTO v_readiness
    FROM topic_mastery tm
    JOIN topics t ON tm.topic_id = t.id
    WHERE tm.user_id = p_user_id
      AND t.curriculum_id = p_curriculum_id;

    RETURN LEAST(1.0, v_readiness);
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE boards IS 'Educational boards (CBSE, State boards, etc.)';
COMMENT ON TABLE subjects IS 'Academic subjects (Math, Science, etc.)';
COMMENT ON TABLE curricula IS 'Board + Subject + Class combinations';
COMMENT ON TABLE topics IS 'Hierarchical chapter/topic structure';
COMMENT ON TABLE question_patterns IS 'Reusable question templates with variable substitution';
COMMENT ON TABLE translations IS 'Multi-language content for vernacular support';
COMMENT ON TABLE student_curriculum_progress IS 'Student enrollment and overall progress';
COMMENT ON TABLE topic_mastery IS 'Granular topic-level mastery tracking';
COMMENT ON TABLE student_gamification IS 'XP, levels, streaks for engagement';
COMMENT ON TABLE achievements IS 'Badge definitions';
COMMENT ON TABLE user_achievements IS 'Unlocked badges per student';
COMMENT ON TABLE leaderboard_entries IS 'Competitive rankings (weekly/monthly/all-time)';
COMMENT ON TABLE mock_tests IS 'Simulated board exams';
COMMENT ON TABLE mock_test_attempts IS 'Student attempts on mock tests';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- This schema supports:
-- ✅ Multi-board (CBSE → Karnataka, Kerala, etc.)
-- ✅ Multi-subject (Math → Science, Social Studies)
-- ✅ Multi-class (10 → 11, 12)
-- ✅ Multi-language (English → Hindi, Tamil, Telugu, etc.)
-- ✅ Gamification (XP, streaks, badges, leaderboards)
-- ✅ Mock tests (simulated board exams)
-- ✅ Scalability (indexes, RLS, audit logs)

-- Next steps:
-- 1. Populate topics table with CBSE Class 10 Math chapters
-- 2. Create 60 question_patterns (JSON templates)
-- 3. Seed achievements table with badges
-- 4. Build CurriculumManager service to query this schema
