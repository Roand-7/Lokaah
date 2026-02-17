"""
TranslationService - AI-powered vernacular support for multi-language scaling

Supports translation of:
- Question patterns (template_text, solution_steps, hints)
- Topic names (curriculum topics, subtopics)
- UI elements (labels, messages, navigation)

Languages: Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from uuid import UUID
import json

logger = logging.getLogger(__name__)


# Supported languages with native names
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "हिन्दी (Hindi)",
    "ta": "தமிழ் (Tamil)",
    "te": "తెలుగు (Telugu)",
    "kn": "ಕನ್ನಡ (Kannada)",
    "ml": "മലയാളം (Malayalam)",
    "bn": "বাংলা (Bengali)",
    "mr": "मराठी (Marathi)",
    "gu": "ગુજરાતી (Gujarati)",
}


class TranslationService:
    """
    AI-powered translation service using Gemini 2.0 Flash

    Cost-effective approach:
    - Gemini 2.0 Flash: $0.075 per 1M input tokens, $0.30 per 1M output
    - Average translation: 100 input + 100 output tokens = $0.0000375 per translation
    - 10,000 translations = $0.375 (vs Google Translate API: $20/1M chars)

    Features:
    - Context-aware translation (maintains educational tone)
    - Database caching (translate once, use forever)
    - Batch translation (multiple strings in single API call)
    - Fallback to English if translation fails
    """

    def __init__(self, gemini_client, supabase_client):
        """
        Args:
            gemini_client: Google GenAI client
            supabase_client: Supabase database client
        """
        self.gemini = gemini_client
        self.db = supabase_client
        self._cache: Dict[str, str] = {}  # In-memory cache
        self._load_cache()

    def _load_cache(self):
        """Load frequently used translations into memory"""
        try:
            # Load last 1000 translations
            result = self.db.table('translations')\
                .select('source_text, target_language, translated_text')\
                .order('usage_count', desc=True)\
                .limit(1000)\
                .execute()

            if result.data:
                for row in result.data:
                    cache_key = f"{row['source_text']}:{row['target_language']}"
                    self._cache[cache_key] = row['translated_text']

                logger.info(f"Loaded {len(self._cache)} translations into cache")
        except Exception as exc:
            logger.warning(f"Failed to load translation cache: {exc}")

    async def translate(
        self,
        text: str,
        target_language: str,
        context: str = "educational",
        source_language: str = "en"
    ) -> str:
        """
        Translate text to target language

        Args:
            text: Text to translate
            target_language: ISO 639-1 code (hi, ta, te, kn, ml, bn, mr, gu)
            context: Context hint for better translation (educational, mathematical, ui)
            source_language: Source language code (default: en)

        Returns:
            Translated text (or original if target is English or translation fails)
        """
        # Return original if target is English
        if target_language == "en" or target_language == source_language:
            return text

        # Check cache
        cache_key = f"{text}:{target_language}"
        if cache_key in self._cache:
            await self._increment_usage(text, target_language)
            return self._cache[cache_key]

        # Check database
        db_translation = await self._get_from_db(text, target_language)
        if db_translation:
            self._cache[cache_key] = db_translation
            await self._increment_usage(text, target_language)
            return db_translation

        # Translate using Gemini
        try:
            translated = await self._translate_with_gemini(
                text, target_language, context, source_language
            )

            # Save to database
            await self._save_to_db(text, target_language, translated, context, source_language)

            # Update cache
            self._cache[cache_key] = translated

            return translated

        except Exception as exc:
            logger.error(f"Translation failed for '{text}' to {target_language}: {exc}")
            return text  # Fallback to original

    async def translate_batch(
        self,
        texts: List[str],
        target_language: str,
        context: str = "educational",
        source_language: str = "en"
    ) -> Dict[str, str]:
        """
        Translate multiple texts in a single API call (more efficient)

        Args:
            texts: List of texts to translate
            target_language: Target language code
            context: Context hint
            source_language: Source language code

        Returns:
            Dict mapping original text to translated text
        """
        if target_language == "en":
            return {text: text for text in texts}

        results = {}
        to_translate = []

        # Check cache first
        for text in texts:
            cache_key = f"{text}:{target_language}"
            if cache_key in self._cache:
                results[text] = self._cache[cache_key]
                await self._increment_usage(text, target_language)
            else:
                to_translate.append(text)

        # Translate remaining texts
        if to_translate:
            try:
                translated = await self._translate_batch_with_gemini(
                    to_translate, target_language, context, source_language
                )

                # Save and cache
                for original, translated_text in zip(to_translate, translated):
                    results[original] = translated_text
                    self._cache[f"{original}:{target_language}"] = translated_text
                    await self._save_to_db(
                        original, target_language, translated_text, context, source_language
                    )

            except Exception as exc:
                logger.error(f"Batch translation failed: {exc}")
                # Fallback to original texts
                for text in to_translate:
                    results[text] = text

        return results

    async def translate_pattern(
        self,
        pattern_data: Dict[str, Any],
        target_language: str
    ) -> Dict[str, Any]:
        """
        Translate a question pattern to target language

        Translates:
        - template_text
        - solution_template (list of steps)
        - socratic_hints (hint and nudge for each level)

        Args:
            pattern_data: Pattern dictionary
            target_language: Target language code

        Returns:
            Translated pattern data
        """
        if target_language == "en":
            return pattern_data

        translated = pattern_data.copy()

        # Translate template text
        translated['template_text'] = await self.translate(
            pattern_data['template_text'],
            target_language,
            context="mathematical"
        )

        # Translate solution steps
        if 'solution_template' in pattern_data:
            translated['solution_template'] = [
                await self.translate(step, target_language, context="mathematical")
                for step in pattern_data['solution_template']
            ]

        # Translate socratic hints
        if 'socratic_hints' in pattern_data:
            translated_hints = []
            for hint in pattern_data['socratic_hints']:
                translated_hints.append({
                    'level': hint['level'],
                    'hint': await self.translate(hint['hint'], target_language, context="educational"),
                    'nudge': await self.translate(hint['nudge'], target_language, context="educational")
                })
            translated['socratic_hints'] = translated_hints

        # Translate answer template
        if 'answer_template' in pattern_data:
            translated['answer_template'] = await self.translate(
                pattern_data['answer_template'],
                target_language,
                context="mathematical"
            )

        return translated

    async def translate_topic(
        self,
        topic_data: Dict[str, Any],
        target_language: str
    ) -> Dict[str, Any]:
        """
        Translate a topic/curriculum item

        Args:
            topic_data: Topic dictionary with 'name', 'description', etc.
            target_language: Target language code

        Returns:
            Translated topic data
        """
        if target_language == "en":
            return topic_data

        translated = topic_data.copy()

        if 'name' in topic_data:
            translated['name'] = await self.translate(
                topic_data['name'],
                target_language,
                context="educational"
            )

        if 'description' in topic_data and topic_data['description']:
            translated['description'] = await self.translate(
                topic_data['description'],
                target_language,
                context="educational"
            )

        if 'learning_objectives' in topic_data and topic_data['learning_objectives']:
            translated['learning_objectives'] = [
                await self.translate(obj, target_language, context="educational")
                for obj in topic_data['learning_objectives']
            ]

        return translated

    async def _translate_with_gemini(
        self,
        text: str,
        target_language: str,
        context: str,
        source_language: str
    ) -> str:
        """Translate using Gemini 2.0 Flash"""
        target_lang_name = SUPPORTED_LANGUAGES.get(target_language, target_language)

        prompt = f"""Translate the following {context} text from English to {target_lang_name}.

IMPORTANT INSTRUCTIONS:
1. Maintain the exact meaning and educational tone
2. Preserve mathematical symbols and LaTeX notation (x², √, π, etc.)
3. Keep variable placeholders intact ({{a}}, {{b}}, {{result}}, etc.)
4. Use formal educational language appropriate for Class 10 students
5. Return ONLY the translated text, no explanations

Text to translate:
{text}

Translation:"""

        try:
            response = self.gemini.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt,
                config={
                    'temperature': 0.3,  # Low temperature for consistent translations
                    'max_output_tokens': 500
                }
            )

            translated = response.text.strip()

            # Remove quotes if Gemini added them
            if translated.startswith('"') and translated.endswith('"'):
                translated = translated[1:-1]

            return translated

        except Exception as exc:
            logger.error(f"Gemini translation failed: {exc}")
            raise

    async def _translate_batch_with_gemini(
        self,
        texts: List[str],
        target_language: str,
        context: str,
        source_language: str
    ) -> List[str]:
        """Translate multiple texts in single API call"""
        target_lang_name = SUPPORTED_LANGUAGES.get(target_language, target_language)

        # Format texts as numbered list
        texts_formatted = "\n".join([f"{i+1}. {text}" for i, text in enumerate(texts)])

        prompt = f"""Translate the following {context} texts from English to {target_lang_name}.

IMPORTANT INSTRUCTIONS:
1. Maintain exact meanings and educational tone
2. Preserve mathematical symbols and LaTeX notation
3. Keep variable placeholders intact ({{a}}, {{b}}, etc.)
4. Return translations in same numbered format
5. One translation per line

Texts to translate:
{texts_formatted}

Translations:"""

        try:
            response = self.gemini.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt,
                config={
                    'temperature': 0.3,
                    'max_output_tokens': 2000
                }
            )

            # Parse numbered output
            translated_lines = response.text.strip().split('\n')
            translations = []

            for line in translated_lines:
                # Remove numbering (e.g., "1. " or "1) ")
                cleaned = line.strip()
                if cleaned and len(cleaned) > 2:
                    # Remove "1. " or "1) " prefix
                    if cleaned[0].isdigit() and cleaned[1] in ['.', ')']:
                        cleaned = cleaned[2:].strip()
                    translations.append(cleaned)

            # Ensure we have same number of translations
            if len(translations) != len(texts):
                logger.warning(f"Translation count mismatch: {len(translations)} != {len(texts)}")
                # Pad with original texts if needed
                while len(translations) < len(texts):
                    translations.append(texts[len(translations)])

            return translations[:len(texts)]

        except Exception as exc:
            logger.error(f"Batch translation failed: {exc}")
            raise

    async def _get_from_db(self, text: str, target_language: str) -> Optional[str]:
        """Get translation from database"""
        try:
            result = self.db.table('translations')\
                .select('translated_text')\
                .eq('source_text', text)\
                .eq('target_language', target_language)\
                .single()\
                .execute()

            return result.data['translated_text'] if result.data else None

        except Exception:
            return None

    async def _save_to_db(
        self,
        source_text: str,
        target_language: str,
        translated_text: str,
        context: str,
        source_language: str
    ):
        """Save translation to database"""
        try:
            self.db.table('translations').upsert({
                'source_text': source_text,
                'source_language': source_language,
                'target_language': target_language,
                'translated_text': translated_text,
                'context': context,
                'usage_count': 1,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }, on_conflict='source_text,target_language').execute()

        except Exception as exc:
            logger.error(f"Failed to save translation: {exc}")

    async def _increment_usage(self, text: str, target_language: str):
        """Increment usage count for cache optimization"""
        try:
            self.db.rpc('increment_translation_usage', {
                'p_source_text': text,
                'p_target_language': target_language
            }).execute()
        except Exception:
            pass  # Non-critical

    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return SUPPORTED_LANGUAGES.copy()

    async def get_translation_stats(self) -> Dict[str, Any]:
        """Get translation statistics"""
        try:
            result = self.db.table('translations')\
                .select('target_language', count='exact')\
                .execute()

            stats = {
                'total_translations': result.count if hasattr(result, 'count') else 0,
                'cached_in_memory': len(self._cache),
                'supported_languages': len(SUPPORTED_LANGUAGES),
                'languages': list(SUPPORTED_LANGUAGES.keys())
            }

            return stats

        except Exception as exc:
            logger.error(f"Failed to get translation stats: {exc}")
            return {
                'total_translations': 0,
                'cached_in_memory': len(self._cache),
                'supported_languages': len(SUPPORTED_LANGUAGES)
            }


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_translation_service: Optional[TranslationService] = None


def get_translation_service(gemini_client, supabase_client) -> TranslationService:
    """Get singleton instance of TranslationService"""
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService(gemini_client, supabase_client)
    return _translation_service
