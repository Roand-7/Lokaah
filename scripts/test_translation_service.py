"""
Test TranslationService - Verify AI-powered vernacular translation
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.translation_service import TranslationService, SUPPORTED_LANGUAGES


class MockGeminiClient:
    """Mock Gemini client for testing without API calls"""

    class Models:
        @staticmethod
        def generate_content(model, contents, config):
            # Simulate translation (just add language prefix)
            text = contents.split("Text to translate:")[-1].split("Translation:")[0].strip()
            target_lang = contents.split("to ")[-1].split(".")[0].strip()

            class Response:
                text = f"[{target_lang}] {text}"

            return Response()

    def __init__(self):
        self.models = MockGeminiClient.Models()


class MockSupabaseClient:
    """Mock Supabase client for testing"""

    def __init__(self):
        self._data = {}

    def table(self, name):
        return self

    def select(self, *args, **kwargs):
        return self

    def eq(self, *args, **kwargs):
        return self

    def single(self):
        return self

    def execute(self):
        class Result:
            data = None
            count = 0

        return Result()

    def upsert(self, data, **kwargs):
        return self

    def rpc(self, name, params):
        return self

    def order(self, *args, **kwargs):
        return self

    def limit(self, n):
        return self


async def test_translation_service():
    """Test TranslationService functionality"""
    print("\n" + "="*60)
    print("TRANSLATION SERVICE TEST")
    print("="*60)

    # Initialize service with mocks
    gemini = MockGeminiClient()
    supabase = MockSupabaseClient()

    service = TranslationService(gemini, supabase)

    print("\n1. Testing supported languages:")
    languages = service.get_supported_languages()
    for code, name in languages.items():
        print(f"   {code}: {name}")

    print(f"\n   Total: {len(languages)} languages")

    print("\n2. Testing single translation:")
    text = "Find the nature of the roots of the quadratic equation"
    target = "hi"

    translated = await service.translate(text, target, context="mathematical")
    print(f"   Original (en): {text}")
    print(f"   Translated ({target}): {translated}")

    print("\n3. Testing batch translation:")
    texts = [
        "Step 1: Identify the given information",
        "Step 2: Apply the relevant formula",
        "Step 3: Calculate the result"
    ]

    translations = await service.translate_batch(texts, "ta", context="educational")
    for original, translated in translations.items():
        print(f"   {original[:40]}... -> {translated[:40]}...")

    print("\n4. Testing pattern translation:")
    pattern = {
        "template_text": "Solve the equation {a}x + {b} = 0",
        "solution_template": [
            "Given: {a}x + {b} = 0",
            "Subtract {b} from both sides",
            "Divide by {a}",
            "x = -{b}/{a}"
        ],
        "socratic_hints": [
            {"level": 1, "hint": "What is the first step?", "nudge": "Isolate the variable"},
            {"level": 2, "hint": "How do you isolate x?", "nudge": "Move constant to other side"}
        ],
        "answer_template": "x = {result}"
    }

    translated_pattern = await service.translate_pattern(pattern, "te")
    print(f"   Original template: {pattern['template_text']}")
    print(f"   Translated (te): {translated_pattern['template_text']}")
    print(f"   Original hint: {pattern['socratic_hints'][0]['hint']}")
    print(f"   Translated hint: {translated_pattern['socratic_hints'][0]['hint']}")

    print("\n5. Testing topic translation:")
    topic = {
        "name": "Quadratic Equations",
        "description": "Study of equations of the form ax² + bx + c = 0",
        "learning_objectives": [
            "Understand the standard form of quadratic equations",
            "Learn to solve using different methods",
            "Determine nature of roots using discriminant"
        ]
    }

    translated_topic = await service.translate_topic(topic, "kn")
    print(f"   Original topic: {topic['name']}")
    print(f"   Translated (kn): {translated_topic['name']}")
    print(f"   Original objective: {topic['learning_objectives'][0]}")
    print(f"   Translated objective: {translated_topic['learning_objectives'][0]}")

    print("\n6. Testing statistics:")
    stats = await service.get_translation_stats()
    print(f"   Total translations in DB: {stats['total_translations']}")
    print(f"   Cached in memory: {stats['cached_in_memory']}")
    print(f"   Supported languages: {stats['supported_languages']}")

    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print("\nNOTE: This test uses mocked clients.")
    print("For real testing, initialize with actual Gemini and Supabase clients.")
    print("\nTo test with real Gemini:")
    print("  from google import genai")
    print("  from app.database import get_db")
    print("  service = TranslationService(genai.Client(api_key=...), get_db())")


if __name__ == "__main__":
    asyncio.run(test_translation_service())
