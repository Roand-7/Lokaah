-- Translation Service RPC Functions (FIXED)
-- Updated to match the entity-based translations table schema from migration 002

-- Function: Get translations for an entity
CREATE OR REPLACE FUNCTION get_entity_translations(
    p_entity_type TEXT,
    p_entity_id UUID,
    p_language_code TEXT DEFAULT NULL
) RETURNS TABLE (
    field_name TEXT,
    language_code TEXT,
    content JSONB,
    translation_source TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.field_name,
        t.language_code,
        t.content,
        t.translation_source
    FROM translations t
    WHERE
        t.entity_type = p_entity_type
        AND t.entity_id = p_entity_id
        AND (p_language_code IS NULL OR t.language_code = p_language_code);
END;
$$ LANGUAGE plpgsql;

-- Function: Upsert translation
CREATE OR REPLACE FUNCTION upsert_translation(
    p_entity_type TEXT,
    p_entity_id UUID,
    p_language_code TEXT,
    p_field_name TEXT,
    p_content JSONB,
    p_translation_source TEXT DEFAULT 'ai',
    p_quality_score FLOAT DEFAULT NULL,
    p_translated_by UUID DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    translation_id UUID;
BEGIN
    INSERT INTO translations (
        entity_type,
        entity_id,
        language_code,
        field_name,
        content,
        translation_source,
        quality_score,
        translated_by
    ) VALUES (
        p_entity_type,
        p_entity_id,
        p_language_code,
        p_field_name,
        p_content,
        p_translation_source,
        p_quality_score,
        p_translated_by
    )
    ON CONFLICT (entity_type, entity_id, language_code, field_name)
    DO UPDATE SET
        content = EXCLUDED.content,
        translation_source = EXCLUDED.translation_source,
        quality_score = EXCLUDED.quality_score,
        translated_by = EXCLUDED.translated_by,
        updated_at = NOW()
    RETURNING id INTO translation_id;

    RETURN translation_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Bulk get translations for multiple entities
CREATE OR REPLACE FUNCTION get_bulk_translations(
    p_entity_type TEXT,
    p_entity_ids UUID[],
    p_language_code TEXT
) RETURNS TABLE (
    entity_id UUID,
    field_name TEXT,
    content JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.entity_id,
        t.field_name,
        t.content
    FROM translations t
    WHERE
        t.entity_type = p_entity_type
        AND t.entity_id = ANY(p_entity_ids)
        AND t.language_code = p_language_code;
END;
$$ LANGUAGE plpgsql;

-- Indexes for faster translation lookups
CREATE INDEX IF NOT EXISTS idx_translations_entity_lookup
    ON translations(entity_type, entity_id, language_code);

CREATE INDEX IF NOT EXISTS idx_translations_language
    ON translations(language_code);

CREATE INDEX IF NOT EXISTS idx_translations_quality
    ON translations(quality_score DESC)
    WHERE quality_score IS NOT NULL;

-- Comments
COMMENT ON FUNCTION get_entity_translations IS
    'Retrieves all translations for a given entity and optional language';

COMMENT ON FUNCTION upsert_translation IS
    'Inserts or updates a translation for an entity field';

COMMENT ON FUNCTION get_bulk_translations IS
    'Retrieves translations for multiple entities at once (performance optimization)';
