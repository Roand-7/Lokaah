-- Translation Service RPC Functions
-- Helper functions for translation usage tracking and optimization

-- Function: Increment translation usage count
CREATE OR REPLACE FUNCTION increment_translation_usage(
    p_source_text TEXT,
    p_target_language TEXT
) RETURNS VOID AS $$
BEGIN
    UPDATE translations
    SET
        usage_count = usage_count + 1,
        updated_at = NOW()
    WHERE
        source_text = p_source_text
        AND target_language = p_target_language;
END;
$$ LANGUAGE plpgsql;

-- Function: Get most used translations (for cache warming)
CREATE OR REPLACE FUNCTION get_hot_translations(
    p_limit INTEGER DEFAULT 1000
) RETURNS TABLE (
    source_text TEXT,
    target_language TEXT,
    translated_text TEXT,
    usage_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.source_text,
        t.target_language,
        t.translated_text,
        t.usage_count
    FROM translations t
    ORDER BY t.usage_count DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function: Clean old unused translations (maintenance)
CREATE OR REPLACE FUNCTION clean_unused_translations(
    p_days_old INTEGER DEFAULT 90,
    p_min_usage INTEGER DEFAULT 1
) RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    WITH deleted AS (
        DELETE FROM translations
        WHERE
            usage_count < p_min_usage
            AND created_at < NOW() - (p_days_old || ' days')::INTERVAL
        RETURNING *
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Index for faster translation lookups
CREATE INDEX IF NOT EXISTS idx_translations_source_target
    ON translations(source_text, target_language);

CREATE INDEX IF NOT EXISTS idx_translations_usage
    ON translations(usage_count DESC);

-- Comment
COMMENT ON FUNCTION increment_translation_usage IS
    'Increments usage count for translation cache optimization';

COMMENT ON FUNCTION get_hot_translations IS
    'Returns most frequently used translations for cache warming';

COMMENT ON FUNCTION clean_unused_translations IS
    'Removes old unused translations to keep database lean';
