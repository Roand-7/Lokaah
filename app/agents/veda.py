from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import json
import logging
import os
import re
import time


logger = logging.getLogger(__name__)


class StudentState(str, Enum):
    HOOK = "hook"
    EXPLORE = "explore"
    CONSOLIDATE = "consolidate"
    APPLY = "apply"
    REFLECT = "reflect"


class DifficultyLevel(str, Enum):
    STRUGGLING = "struggling"
    ON_TRACK = "on_track"
    EXCELLING = "excelling"


@dataclass
class TeachingContext:
    current_state: StudentState = StudentState.HOOK
    difficulty: DifficultyLevel = DifficultyLevel.ON_TRACK
    concept_mastery: Dict[str, float] = field(default_factory=dict)
    attempts_on_current: int = 0
    last_hint_given: Optional[str] = None
    visual_aids_shown: List[str] = field(default_factory=list)
    last_interaction_ts: float = field(default_factory=lambda: time.time())

    def update_mastery(self, concept: str, success: bool) -> None:
        current = self.concept_mastery.get(concept, 0.5)
        if success:
            updated = min(1.0, current + 0.15)
        else:
            updated = max(0.0, current - 0.10)
        self.concept_mastery[concept] = updated


from app.services.diagram_generator import DiagramGenerator
from app.services.exam_database import ExamDatabase, ExamQuestion, build_exam_database
from app.services.math_renderer import MathRenderer
from app.services.pdf_generator import PDFGenerator
from app.core.config import settings


@dataclass
class VedaConfig:
    model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    temperature: float = 0.7
    max_tokens: int = 1500
    history_limit: int = 5
    exam_board_default: str = "CBSE"
    retry_on_parse_error: bool = True


class VedaAgent:
    """
    VEDA - Socratic, exam-focused tutoring agent with structured pedagogy.
    """

    def __init__(
        self,
        client: Optional[Any] = None,
        config: Optional[VedaConfig] = None,
        math_renderer: Optional[MathRenderer] = None,
        diagram_generator: Optional[DiagramGenerator] = None,
        exam_db: Optional[ExamDatabase] = None,
        pdf_generator: Optional[PDFGenerator] = None,
    ) -> None:
        self.config = config or VedaConfig()
        self.client = client or self._init_gemini_client()
        self.math_renderer = math_renderer or MathRenderer()
        self.diagram_gen = diagram_generator or DiagramGenerator()
        self.exam_db = exam_db or build_exam_database()
        self.pdf_generator = pdf_generator or PDFGenerator()
        self.contexts: Dict[str, TeachingContext] = {}

    def _init_gemini_client(self) -> Optional[Any]:
        api_key = settings.GEMINI_API_KEY
        try:
            from google import genai  # type: ignore

            if api_key:
                logger.info("VEDA Gemini client initialized using API key.")
                return genai.Client(api_key=api_key)

            if settings.GOOGLE_APPLICATION_CREDENTIALS and settings.GOOGLE_CLOUD_PROJECT:
                os.environ.setdefault(
                    "GOOGLE_APPLICATION_CREDENTIALS",
                    settings.GOOGLE_APPLICATION_CREDENTIALS,
                )
                logger.info("VEDA Gemini client initialized using Vertex AI credentials.")
                return genai.Client(
                    vertexai=True,
                    project=settings.GOOGLE_CLOUD_PROJECT,
                    location=settings.GOOGLE_CLOUD_LOCATION,
                )

            logger.warning("VEDA Gemini client not initialized: missing auth configuration.")
            return None
        except Exception as exc:
            logger.exception("Failed to initialize Gemini client for VEDA: %s", exc)
            return None

    def _get_or_create_context(self, session_id: str) -> TeachingContext:
        if session_id not in self.contexts:
            self.contexts[session_id] = TeachingContext()
        return self.contexts[session_id]

    def _detect_language_and_gender(
        self,
        message: str,
        explicit_language: Optional[str] = None,
        explicit_gender: Optional[str] = None,
    ) -> Tuple[str, str]:
        if explicit_language:
            lang = explicit_language
        else:
            kannada_chars = set(
                "\u0C85\u0C86\u0C87\u0C88\u0C89\u0C8A\u0C8B\u0C8E\u0C8F\u0C90\u0C92\u0C93"
                "\u0C94\u0C95\u0C96\u0C97\u0C98\u0C99\u0C9A\u0C9B\u0C9C\u0C9D\u0C9E"
                "\u0C9F\u0CA0\u0CA1\u0CA2\u0CA3\u0CA4\u0CA5\u0CA6\u0CA7\u0CA8\u0CAA"
                "\u0CAB\u0CAC\u0CAD\u0CAE\u0CAF\u0CB0\u0CB2\u0CB5\u0CB6\u0CB7\u0CB8\u0CB9\u0CB3"
            )
            malayalam_chars = set(
                "\u0D05\u0D06\u0D07\u0D08\u0D09\u0D0A\u0D0B\u0D0E\u0D0F\u0D10\u0D12\u0D13"
                "\u0D14\u0D15\u0D16\u0D17\u0D18\u0D19\u0D1A\u0D1B\u0D1C\u0D1D\u0D1E"
                "\u0D1F\u0D20\u0D21\u0D22\u0D23\u0D24\u0D25\u0D26\u0D27\u0D28\u0D2A"
                "\u0D2B\u0D2C\u0D2D\u0D2E\u0D2F\u0D30\u0D32\u0D35\u0D36\u0D37\u0D38\u0D39\u0D33\u0D34\u0D31"
            )
            hindi_chars = set(
                "\u0905\u0906\u0907\u0908\u0909\u090A\u090B\u090F\u0910\u0913\u0914\u0915\u0916"
                "\u0917\u0918\u0919\u091A\u091B\u091C\u091D\u091E\u091F\u0920\u0921\u0922\u0923"
                "\u0924\u0925\u0926\u0927\u0928\u092A\u092B\u092C\u092D\u092E\u092F\u0930\u0932\u0935\u0936\u0937\u0938\u0939"
            )
            msg_set = set(message)
            # Detect language from script characters
            tamil_chars = set("அஆஇஈஉஊஎஏஐஒஓஔகஙசஜஞடணதநனபமயரலவழளறனஃ")
            telugu_chars = set("అఆఇఈఉఊఋఎఏఐఒఓఔకఖగఘఙచఛజఝఞటఠడఢణతథదధనపఫబభమయరలవశషసహళ")
            bengali_chars = set("অআইঈউঊঋএঐওঔকখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহড়ঢ়য়ং")
            marathi_chars = set("अआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसहळ")
            gujarati_chars = set("અઆઇઈઉઊઋએઐઓઔકખગઘઙચછજઝઞટઠડઢણતથદધનપફબભમયરલવશષસહળ")

            if msg_set & tamil_chars:
                lang = "tanglish"
            elif msg_set & telugu_chars:
                lang = "tenglish"
            elif msg_set & kannada_chars:
                lang = "kanglish"
            elif msg_set & malayalam_chars:
                lang = "manglish"
            elif msg_set & bengali_chars:
                lang = "benglish"
            elif msg_set & marathi_chars:
                lang = "marathglish"
            elif msg_set & gujarati_chars:
                lang = "gujarlish"
            elif msg_set & hindi_chars:
                lang = "hinglish"
            else:
                lang = "english"  # Default to English

        gender = explicit_gender or "neutral"
        return lang, gender

    def _get_vernacular_config(self, language: str, gender: str) -> Dict[str, Any]:
        configs: Dict[str, Dict[str, Dict[str, Any]]] = {
            "english": {
                "male": {
                    "address": "friend",
                    "encouragement": ["Great", "Excellent", "Well done", "Perfect"],
                    "empathy": "It's okay, everyone finds this challenging at first",
                    "challenge": "Let's try again. You can do this.",
                    "exam_phrase": "This might appear in your board exam",
                    "formula_intro": "Here's the formula:",
                    "visual_prompt": "Let's look at a diagram.",
                    "stuck_recovery": "Let me explain this from a different angle",
                },
                "female": {
                    "address": "friend",
                    "encouragement": ["Excellent", "Amazing", "Very good", "Wonderful"],
                    "empathy": "I understand, this can be tricky",
                    "challenge": "You can do this. Let's try once more.",
                    "exam_phrase": "This could appear in your exam",
                    "formula_intro": "Here's the formula:",
                    "visual_prompt": "Let's visualize this with a diagram.",
                    "stuck_recovery": "Let me show you another way to think about this",
                },
                "neutral": {
                    "address": "friend",
                    "encouragement": ["Good", "Nice", "Well done", "Great"],
                    "empathy": "No problem, this is a bit challenging",
                    "challenge": "Let's try again together.",
                    "exam_phrase": "This is relevant for your exam",
                    "formula_intro": "Here's the formula:",
                    "visual_prompt": "Let's draw a diagram.",
                    "stuck_recovery": "Let me approach this differently",
                },
            },
            "hinglish": {
                "male": {
                    "address": "bhai",
                    "encouragement": ["Shabash", "Mast", "Ekdum sahi", "Killer"],
                    "empathy": "Koi nahi, shuru mein sabko tough lagta hai",
                    "challenge": "Ek aur try kar. Tu kar sakta hai.",
                    "exam_phrase": "Board exam mein yeh zaroor aayega",
                    "formula_intro": "Formula note kar:",
                    "visual_prompt": "Diagram dekhte hain.",
                    "stuck_recovery": "Ruk, alag tareeke se samjhata hoon",
                },
                "female": {
                    "address": "dost",
                    "encouragement": ["Zabardast", "Bahut accha", "Perfect", "Super"],
                    "empathy": "Samajh sakti hoon, thoda tricky hai",
                    "challenge": "Tum kar sakti ho. Last try.",
                    "exam_phrase": "Exam mein yeh question aa sakta hai",
                    "formula_intro": "Formula note kar lo:",
                    "visual_prompt": "Diagram banate hain.",
                    "stuck_recovery": "Ruko, dusre angle se dekhte hain",
                },
                "neutral": {
                    "address": "dost",
                    "encouragement": ["Good", "Nice", "Solid", "Great"],
                    "empathy": "Koi nahi, thoda tricky hai",
                    "challenge": "Ek aur try karte hain.",
                    "exam_phrase": "Exam mein yeh aa sakta hai",
                    "formula_intro": "Formula note karo:",
                    "visual_prompt": "Diagram dekhte hain.",
                    "stuck_recovery": "Ruk, alag tareeke se dekhte hain",
                },
            },
            "kanglish": {
                "male": {
                    "address": "machaa",
                    "encouragement": ["Sakkath", "Channagide", "Killer", "Super"],
                    "empathy": "Parvaagilla, ellaarigu tough aagutte",
                    "challenge": "Maadu, nodona. Ninge aaguthe.",
                    "exam_phrase": "Board exam alli idu pakka barutte",
                    "formula_intro": "Formula note maadu:",
                    "visual_prompt": "Diagram nodona.",
                    "stuck_recovery": "Wait, bere tare helthini",
                },
                "neutral": {
                    "address": "dost",
                    "encouragement": ["Sakkath", "Channagide", "Super"],
                    "empathy": "Parvaagilla, tough aagutte",
                    "challenge": "Maadu, nodona.",
                    "exam_phrase": "Exam alli idu barabahudu",
                    "formula_intro": "Formula note maadu:",
                    "visual_prompt": "Diagram nodona.",
                    "stuck_recovery": "Wait, bere tare helthini",
                },
            },
            "manglish": {
                "neutral": {
                    "address": "dost",
                    "encouragement": ["Super", "Valare nannay", "Killer"],
                    "empathy": "Samasya illa, ithu kurachu tough aanu",
                    "challenge": "Nee cheyyum, njan viswasikkunnu",
                    "exam_phrase": "Exam-il ithu varam",
                    "formula_intro": "Formula note cheyyu:",
                    "visual_prompt": "Diagram nokkam.",
                    "stuck_recovery": "Nirthu, vere reethiyil parayam",
                }
            },
            "tanglish": {  # Tamil + English
                "neutral": {
                    "address": "friend",
                    "encouragement": ["Nalla", "Romba nalla", "Super", "Semma"],
                    "empathy": "Paravala, koncham kashtam dhaan",
                    "challenge": "Nee pannalam, try pannu",
                    "exam_phrase": "Exam-la idhu varumnu ninaikkaren",
                    "formula_intro": "Formula ezhudhu:",
                    "visual_prompt": "Diagram paakalam.",
                    "stuck_recovery": "Wait, vera method-la solren",
                }
            },
            "tenglish": {  # Telugu + English
                "neutral": {
                    "address": "friend",
                    "encouragement": ["Baagundi", "Chala baagundi", "Super", "Awesome"],
                    "empathy": "Parledhu, konchem tough undi",
                    "challenge": "Nevu cheyagalavu, try cheyyi",
                    "exam_phrase": "Exam lo idhi raavachu",
                    "formula_intro": "Formula raasuko:",
                    "visual_prompt": "Diagram choodham.",
                    "stuck_recovery": "Wait, vere vidham ga cheptha",
                }
            },
            "benglish": {  # Bengali + English
                "neutral": {
                    "address": "bondhu",
                    "encouragement": ["Bhalo", "Khub bhalo", "Darun", "Awesome"],
                    "empathy": "Kono bepar nai, ektu kothin",
                    "challenge": "Tumi parbe, try koro",
                    "exam_phrase": "Exam-e eta asbe",
                    "formula_intro": "Formula likhe nao:",
                    "visual_prompt": "Diagram dekhbo.",
                    "stuck_recovery": "Darao, onno bhabe bujhai",
                }
            },
            "marathglish": {  # Marathi + English
                "neutral": {
                    "address": "mitra",
                    "encouragement": ["Chan", "Khup chan", "Jabardast", "Super"],
                    "empathy": "Kahi nahi, thoda kathin ahe",
                    "challenge": "Tu karu shaktos, try kar",
                    "exam_phrase": "Exam madhe he yenar",
                    "formula_intro": "Formula lihun thev:",
                    "visual_prompt": "Diagram baghuya.",
                    "stuck_recovery": "Thamba, veglyane samjato",
                }
            },
            "gujarlish": {  # Gujarati + English
                "neutral": {
                    "address": "dost",
                    "encouragement": ["Saru", "Khub saru", "Badhiya", "Super"],
                    "empathy": "Koi vaat nathi, thodu difficult chhe",
                    "challenge": "Tame kari shakso, try karo",
                    "exam_phrase": "Exam ma aa aavse",
                    "formula_intro": "Formula lakhjo:",
                    "visual_prompt": "Diagram jova.",
                    "stuck_recovery": "Roko, biji rite samjavu",
                }
            },
        }

        return (
            configs.get(language, {}).get(gender)
            or configs.get(language, {}).get("neutral")
            or configs["hinglish"]["neutral"]
        )

    def _build_structured_prompt(
        self,
        context: TeachingContext,
        vernacular: Dict[str, Any],
        topic: Optional[str],
        exam_board: str,
    ) -> str:
        state_instructions = {
            StudentState.HOOK: (
                "STEP 1 - THE HOOK:\n"
                "- Start with relatable real-world scenario (5-10 seconds)\n"
                "- Must connect to student life (sports, food, phone, relationships)\n"
                "- End with curiosity gap: \"But how does this work?\"\n"
                "- No formulas yet. No definitions yet. Just the puzzle.\n"
            ),
            StudentState.EXPLORE: (
                "STEP 2 - GUIDED EXPLORATION:\n"
                "- Ask one specific question at a time\n"
                "- Wait for student response before next step\n"
                "- If wrong: \"Interesting... ek aur baar socho\"\n"
                "- If right: Build on it immediately\n"
                "- Use \"What if...\" to extend thinking\n"
                "- Never say \"No\" or \"Wrong\" - say \"Almost! Dekho...\"\n"
            ),
            StudentState.CONSOLIDATE: (
                "STEP 3 - PATTERN RECOGNITION:\n"
                "- Ask: \"Notice kiya pattern?\"\n"
                "- Help student articulate the rule themselves\n"
                "- Only then introduce formal name or formula\n"
            ),
            StudentState.APPLY: (
                "STEP 4 - EXAM APPLICATION:\n"
                "- Use an actual board question (same type)\n"
                "- Mention marks and attempt rate\n"
                "- Guide through solution step-by-step\n"
                "- Highlight common mistakes\n"
            ),
            StudentState.REFLECT: (
                "STEP 5 - METACOGNITION:\n"
                "- Ask: \"Kaisa laga?\"\n"
                "- Confidence check: \"Ab same type ka kar sakte ho?\"\n"
                "- Celebrate specific growth, not generic praise\n"
            ),
        }

        current_step = state_instructions.get(context.current_state, state_instructions[StudentState.HOOK])

        difficulty_note = ""
        if context.difficulty == DifficultyLevel.STRUGGLING:
            difficulty_note = (
                "STUDENT STRUGGLING - ADAPT:\n"
                "- Give concrete example immediately\n"
                "- Use visual analogy (diagram or real object)\n"
                "- Break into micro-steps\n"
                "- If 2 wrong attempts: give answer with explanation, then similar question\n"
                f"- Recovery phrase: {vernacular['stuck_recovery']}\n"
            )
        elif context.difficulty == DifficultyLevel.EXCELLING:
            difficulty_note = (
                "STUDENT EXCELLING - CHALLENGE:\n"
                "- Ask \"Why does this work?\" not just \"How\"\n"
                "- Connect to advanced concept (preview)\n"
                "- Variation: change sign or boundary\n"
                "- Speed challenge: \"30 seconds mein batao\"\n"
            )

        return (
            "You are VEDA, an elite AI tutor for board exams.\n\n"
            f"CURRENT STATE: {context.current_state.value.upper()}\n"
            f"TOPIC: {topic or 'General'}\n"
            f"STUDENT MASTERY: {json.dumps(context.concept_mastery, indent=2)}\n\n"
            "CORE PRINCIPLE:\n"
            "Be CONVERSATIONAL and CONTEXT-AWARE. Not every message needs an elaborate real-world scenario.\n"
            "- Simple questions deserve simple answers\n"
            "- Follow-ups should build on previous context\n"
            "- Use Socratic method for NEW concepts, not greetings or clarifications\n\n"
            "TEACHING PHILOSOPHY:\n"
            "Guide discovery. Student should feel:\n"
            "1) I figured this out myself.\n"
            "2) This is actually simple.\n"
            "3) I can handle board exams.\n\n"
            f"{current_step}\n"
            f"{difficulty_note}\n"
            "VERNACULAR STYLE:\n"
            f"- Address as: {vernacular['address']}\n"
            f"- Encouragement: {', '.join(vernacular['encouragement'])}\n"
            f"- Empathy: {vernacular['empathy']}\n"
            f"- Challenge: {vernacular['challenge']}\n"
            f"- Exam context: {vernacular['exam_phrase']}\n\n"
            "IMPORTANT: Read the conversation history carefully. If the student is asking a follow-up question "
            "(like 'show me an example' after discussing a topic), stay on that topic and provide what they asked for.\n\n"
            "OUTPUT FORMAT:\n"
            "Respond in this JSON structure (wrapped in markdown):\n"
            "```json\n"
            "{\n"
            "  \"hook\": \"Real-world scenario text (optional for follow-ups)\",\n"
            "  \"question\": \"Socratic question\",\n"
            "  \"visual_needed\": true,\n"
            "  \"visual_description\": \"Diagram description\",\n"
            "  \"formula_latex\": \"LaTeX formula\",\n"
            "  \"encouragement\": \"Specific praise\",\n"
            "  \"next_state\": \"hook/explore/consolidate/apply/reflect\",\n"
            "  \"confidence_update\": {\"concept\": \"name\", \"delta\": 0.15}\n"
            "}\n"
            "```\n"
            "Then add conversational text after the JSON.\n"
        )

    def _analyze_student_input(self, message: str, context: TeachingContext) -> Dict[str, bool]:
        msg_lower = message.lower().strip()
        signals = {
            "repeated_failure": False,
            "rapid_success": False,
            "explicit_visual_request": False,
            "frustration": False,
            "confidence_surge": False,
            "wants_answer_directly": False,
            "is_greeting": False,
            "is_identity_question": False,
            "needs_context": False,
        }
        
        # Detect greetings - simple hellos that need a greeting back, not a lesson
        greetings = ["hi", "hey", "hello", "namaste", "hola", "yo", "sup", "what's up", 
                     "kaise ho", "kya haal", "namaskar", "assalamualaikum", "sat sri akal",
                     "good morning", "good evening", "good afternoon", "good night"]
        if any(msg_lower == g or msg_lower.startswith(g + " ") for g in greetings):
            signals["is_greeting"] = True
        
        # Detect identity questions - "who are you", "what are you", etc.
        identity_questions = ["who are you", "what are you", "kya ho tum", "kaun ho", "tell me about yourself"]
        if any(q in msg_lower for q in identity_questions):
            signals["is_identity_question"] = True
        
        # Detect follow-up requests that need previous context
        followup_phrases = ["show me an example", "give me an example", "can you show", "show example",
                           "another one", "one more", "more examples", "ek aur", "aur dikhao"]
        if any(phrase in msg_lower for phrase in followup_phrases):
            signals["needs_context"] = True
            logger.info(f"needs_context signal set for message: '{message[:50]}'...")

        if context.attempts_on_current >= 3:
            failure_indicators = ["nahi", "wrong", "galat", "confuse", "samajh", "dont know", "no idea"]
            if any(w in msg_lower for w in failure_indicators):
                signals["repeated_failure"] = True

        success_words = ["sahi", "correct", "haan", "yes", "got it", "samajh gaya", "easy", "simple"]
        if any(w in msg_lower for w in success_words) and context.attempts_on_current <= 2:
            signals["rapid_success"] = True

        visual_cues = ["diagram", "dikhao", "show", "draw", "picture", "kaise dikhata hai"]
        if any(w in msg_lower for w in visual_cues):
            signals["explicit_visual_request"] = True

        frustration_words = ["bahut hard", "impossible", "choro", "leave it", "fed up", "irritate"]
        if any(w in msg_lower for w in frustration_words):
            signals["frustration"] = True

        direct_cues = ["seedha batao", "direct answer", "bas answer", "solution do", "batao na"]
        if any(w in msg_lower for w in direct_cues):
            signals["wants_answer_directly"] = True

        return signals

    def _generate_greeting(self, vernacular: Dict[str, Any], language: str) -> str:
        """Generate a friendly greeting response instead of jumping into teaching."""
        import random
        
        greetings = {
            "hinglish": [
                f"Hey {vernacular['address']}! VEDA here — ready to make math simple for you? Kaunsa chapter kar rahe ho?",
                f"Arre {vernacular['address']}! Kaise ho? CBSE math mein kya padhna hai aaj?",
                f"Namaste {vernacular['address']}! Main hoon VEDA — tumhara AI math tutor. Kya seekhna hai?",
                f"Hey! Ready to crack some math? {vernacular['address']}, batao kya help chahiye? Trigonometry? Quadratic?"
            ],
            "kanglish": [
                f"Hey {vernacular['address']}! VEDA here. Yenu kaliyo? Which topic shall we tackle?",
                f"Namaskara {vernacular['address']}! CBSE math easy aagutte, nanna jothe. Yav chapter?"
            ],
            "manglish": [
                f"Hey {vernacular['address']}! VEDA here. Ethra undu? Which chapter are we doing today?"
            ]
        }
        
        lang_greetings = greetings.get(language, greetings["hinglish"])
        return random.choice(lang_greetings)

    def _parse_structured_response(self, raw: str) -> Dict[str, Any]:
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", raw, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON block from LLM response.")

        raw_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if raw_match:
            try:
                return json.loads(raw_match.group(0))
            except json.JSONDecodeError:
                logger.warning("Failed to parse inline JSON from LLM response.")

        return {
            "hook": "",
            "question": "",
            "visual_needed": False,
            "visual_description": "",
            "formula_latex": "",
            "encouragement": "",
            "next_state": None,
            "confidence_update": None,
            "raw": raw,
        }

    def _extract_conversation(self, raw: str) -> str:
        parts = raw.split("```")
        if len(parts) >= 3:
            return parts[-1].strip()
        return raw.strip()

    def _extract_response_text(self, response: Any) -> str:
        text = getattr(response, "text", None)
        if text:
            return str(text).strip()

        try:
            candidates = getattr(response, "candidates", []) or []
            for candidate in candidates:
                content = getattr(candidate, "content", None)
                parts = getattr(content, "parts", []) if content else []
                collected = []
                for part in parts:
                    part_text = getattr(part, "text", None)
                    if part_text:
                        collected.append(str(part_text))
                if collected:
                    return "\n".join(collected).strip()
        except Exception:
            return ""
        return ""

    def _extract_token_usage(self, response: Any) -> Optional[int]:
        usage = getattr(response, "usage_metadata", None)
        if not usage:
            return None
        total = getattr(usage, "total_token_count", None)
        if total is not None:
            return int(total)
        prompt = int(getattr(usage, "prompt_token_count", 0) or 0)
        candidate = int(getattr(usage, "candidates_token_count", 0) or 0)
        total_estimate = prompt + candidate
        return total_estimate if total_estimate > 0 else None

    def _build_gemini_prompt(
        self, system_prompt: str, messages: List[Dict[str, str]]
    ) -> str:
        history_lines: List[str] = []
        for msg in messages[-self.config.history_limit :]:
            role = msg.get("role", "user")
            label = "Student" if role == "user" else "Tutor"
            history_lines.append(f"{label}: {msg.get('content', '')}")
        history_text = "\n".join(history_lines).strip()
        return (
            f"{system_prompt}\n\n"
            "CONVERSATION HISTORY:\n"
            f"{history_text}\n\n"
            "Follow the required JSON format first, then conversational response."
        )

    async def _generate_assets(self, parsed: Dict[str, Any], language: str) -> Dict[str, Any]:
        assets: Dict[str, Any] = {}

        if parsed.get("visual_needed") and parsed.get("visual_description"):
            try:
                diagram = await self.diagram_gen.generate(
                    description=str(parsed["visual_description"]),
                    style="minimal",
                    language=language,
                )
                assets["diagram"] = diagram
            except Exception as exc:
                logger.exception("Diagram generation failed: %s", exc)
                assets["diagram"] = None

        if parsed.get("formula_latex"):
            try:
                render_result = self.math_renderer.render(str(parsed["formula_latex"]))
                assets["formula_html"] = render_result.html
                assets["formula_latex"] = render_result.latex
                assets["formula_engine"] = render_result.engine
            except Exception as exc:
                logger.exception("Math render failed: %s", exc)
                assets["formula_html"] = str(parsed["formula_latex"])

        return assets

    async def _fetch_relevant_exam_question(
        self, chapter: str, board: str, year: int = 2024
    ) -> Optional[Dict[str, Any]]:
        try:
            question = await self.exam_db.get_question(
                chapter=chapter,
                board=board,
                year=year,
                difficulty="medium",
            )
            if not question:
                return None
            return {
                "question_text": question.text,
                "marks": question.marks,
                "year": question.year,
                "set": question.set_number,
                "attempt_rate": question.statistics.get("attempt_rate", 0.0),
                "success_rate": question.statistics.get("avg_score", 0.0),
            }
        except Exception as exc:
            logger.exception("Exam DB fetch failed: %s", exc)
            return None

    async def teach(
        self,
        student_message: str,
        session_id: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        explicit_language: Optional[str] = None,
        explicit_gender: Optional[str] = None,
        topic: Optional[str] = None,
        exam_board: Optional[str] = None,
        current_chapter: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,  # NEW: Gemini tools for autonomous calling
    ) -> Dict[str, Any]:
        context = self._get_or_create_context(session_id)
        context.last_interaction_ts = time.time()

        language, gender = self._detect_language_and_gender(
            student_message, explicit_language, explicit_gender
        )
        vernacular = self._get_vernacular_config(language, gender)
        signals = self._analyze_student_input(student_message, context)

        # Handle simple greetings - don't jump into teaching mode
        if signals["is_greeting"]:
            greeting = self._generate_greeting(vernacular, language)
            return {
                "agent": "veda",
                "session_id": session_id,
                "state": "greeting",
                "difficulty": context.difficulty.value,
                "language": language,
                "text": greeting,
                "socratic_question": "",
                "encouragement": "",
                "has_visual": False,
                "visual_data": None,
                "formula_html": None,
                "exam_question": None,
                "mastery_scores": context.concept_mastery,
                "attempts": context.attempts_on_current,
                "signals": signals,
            }
        
        # Handle identity questions - simple explanation of who VEDA is
        if signals["is_identity_question"]:
            identity_response = (
                f"Hey {vernacular['address']}! I'm VEDA — Your Expert Digital Assistant for board exams. "
                f"I'm here to help you master CBSE math through interactive teaching, practice questions, and personalized guidance. "
                f"I use real-world examples, visual explanations, and Socratic questions to make tough concepts easy. "
                f"Think of me as your friendly AI tutor who's available 24/7! Ready to tackle some math?"
            )
            return {
                "agent": "veda",
                "session_id": session_id,
                "state": "introduction",
                "difficulty": context.difficulty.value,
                "language": language,
                "text": identity_response,
                "socratic_question": "",
                "encouragement": "",
                "has_visual": False,
                "visual_data": None,
                "formula_html": None,
                "exam_question": None,
                "mastery_scores": context.concept_mastery,
                "attempts": context.attempts_on_current,
                "signals": signals,
            }
        
        # Handle follow-up questions that need context from previous conversation
        logger.info(f"Checking context-aware handler: needs_context={signals['needs_context']}, history_len={len(conversation_history) if conversation_history else 0}, student_message='{student_message[:50]}'")
        
        # NOTE: Due to checkpointer issue, conversation_history may only have current message
        # So we ALSO try to extract topic from the user's CURRENT message as fallback
        if signals["needs_context"]:
            # Try to get history context first, but fallback to current message scanning
            has_history = conversation_history and len(conversation_history) > 1
            logger.info(f"Context-aware handler: has_history={has_history}")
            logger.info(f"Context-aware handler triggered! History length: {len(conversation_history)}")
            # Extract the EXACT TOPIC the user asked about (from their last substantive message)
            detected_topic_key = None
            detected_topic_name = "the previous topic"
            
            topic_keywords = {
                "quadratic": "QUADRATIC EQUATIONS",
                "pythagoras": "PYTHAGORAS THEOREM",
                "trigonometry": "TRIGONOMETRY",
                "trigonometric": "TRIGONOMETRY",
                "algebra": "ALGEBRA",
                "coordinate": "COORDINATE GEOMETRY",
                "geometry": "GEOMETRY",
                "polynomial": "POLYNOMIALS",
                "circle": "CIRCLES",
                "triangle": "TRIANGLES",
                "linear": "LINEAR EQUATIONS",
            }
            
            # Search recent messages for topic mentions
            for msg in reversed(conversation_history[-5:]):
                content = msg.get("content", "").lower()
                for keyword, topic_name in topic_keywords.items():
                    if keyword in content:
                        detected_topic_key = keyword
                        detected_topic_name = topic_name
                        break
                if detected_topic_key:
                    break
            logger.info(f"Detected topic: '{detected_topic_name}' (key: {detected_topic_key})")
            
            
            # Use HARDCODED examples for common topics (guarantees correctness!)
            hardcoded_examples = {
                "quadratic": (
                    f"Sure {vernacular['address']}! Here's a quadratic equation example:\n\n"
                    f"**Solve:** x² - 5x + 6 = 0\n\n"
                    f"**Solution:**\n"
                    f"1. Factor the equation: (x - 2)(x - 3) = 0\n"
                    f"2. Set each factor to zero: x - 2 = 0  OR  x - 3 = 0\n"
                    f"3. Solutions: x = 2  or  x = 3\n\n"
                    f"✅ Check: (2)² - 5(2) + 6 = 4 - 10 + 6 = 0 ✓\n\n"
                    f"Try solving: x² + 7x + 10 = 0"
                ),
                "pythagoras": (
                    f"Pakka! Here's a Pythagoras theorem example:\n\n"
                    f"**Problem:** A ladder is 5 meters long. It leans against a wall, with its base 3 meters from the wall. How high up the wall does it reach?\n\n"
                    f"**Solution:**\n"
                    f"1. Use a² + b² = c²\n"
                    f"2. 3² + height² = 5²\n"
                    f"3. 9 + height² = 25\n"
                    f"4. height² = 16\n"
                    f"5. height = 4 meters\n\n"
                    f"Try one: Base = 6m, Hypotenuse = 10m. Find height!"
                ),
                "trigonometry": (
                    f"Here you go {vernacular['address']}!\n\n"
                    f"**Problem:** A kite flies 50 meters directly above the ground. The string makes a 60° angle with the ground. Find the string length.\n\n"
                    f"**Solution:**\n"
                    f"1. sin(60°) = height/string\n"
                    f"2. sin(60°) = √3/2 = 0.866\n"
                    f"3. 0.866 = 50/string\n"
                    f"4. string = 50/0.866 ≈ 57.7 meters\n\n"
                    f"Now try: height = 40m, angle = 45°"
                ),
                "linear": (
                    f"Sure thing! Here's a linear equation example:\n\n"
                    f"**Solve:** 2x + 5 = 11\n\n"
                    f"**Solution:**\n"
                    f"1. Subtract 5 from both sides: 2x = 6\n"
                    f"2. Divide by 2: x = 3\n\n"
                    f"Try solving: 3x - 7 = 14"
                ),
            }
            logger.info(f"Using hardcoded example for '{detected_topic_key}'")
                
            # If we have a hardcoded example for this topic, use it!
            if detected_topic_key in hardcoded_examples:
                return {
                    "agent": "veda",
                    "session_id": session_id,
                    "state": "example_followup",
                    "difficulty": context.difficulty.value,
                    "language": language,
                    "text": hardcoded_examples[detected_topic_key],
                    "socratic_question": "",
                    "encouragement": "",
                    "has_visual": False,
                    "visual_data": None,
                    "formula_html": None,
                    "exam_question": None,
                    "mastery_scores": context.concept_mastery,
                    "attempts": context.attempts_on_current,
                    "signals": signals,
                }
            
            # Fallback to LLM for other topics
            logger.info(f"No hardcoded example for '{detected_topic_name}', using LLM generation")

        if signals["repeated_failure"] or signals["frustration"]:
            context.difficulty = DifficultyLevel.STRUGGLING
            context.current_state = StudentState.HOOK
        elif signals["rapid_success"]:
            context.difficulty = DifficultyLevel.EXCELLING

        system_prompt = self._build_structured_prompt(
            context,
            vernacular,
            topic,
            exam_board or self.config.exam_board_default,
        )

        messages: List[Dict[str, str]] = []
        if conversation_history:
            for msg in conversation_history[-self.config.history_limit :]:
                messages.append(
                    {"role": msg.get("role", "user"), "content": msg.get("content", "")}
                )

        messages.append(
            {
                "role": "user",
                "content": (
                    f"Topic: {topic or 'General'}\n"
                    f"Chapter: {current_chapter or 'Unknown'}\n"
                    f"Student: {student_message}"
                ),
            }
        )

        if not self.client:
            return {
                "agent": "veda",
                "error": True,
                "text": f"{vernacular.get('empathy', 'Koi nahi')}. Technical issue. Try again.",
                "fallback": True,
            }

        try:
            prompt = self._build_gemini_prompt(system_prompt, messages)

            # Build generate_content arguments
            gen_args = {
                "model": self.config.model,
                "contents": prompt,
            }

            # Add tools if provided (Phase 4: Agentic transformation)
            if tools:
                gen_args["tools"] = tools

            response = self.client.models.generate_content(**gen_args)

            # Check for function calls (tool calls)
            function_calls = getattr(response, 'function_calls', None)
            if function_calls and tools:
                # Tool calling mode - return tool execution signal
                tool_calls = []
                for call in function_calls:
                    tool_calls.append({
                        "tool_name": call.name,
                        "args": dict(call.args) if hasattr(call, 'args') else {}
                    })

                return {
                    "agent": "veda",
                    "session_id": session_id,
                    "tool_calls": tool_calls,  # Signal to VedaNode to execute tools
                    "state": "tool_calling",
                    "language": language,
                    "text": "",  # No text when tool calling
                }

            raw_response = self._extract_response_text(response)
            if not raw_response:
                raise ValueError("Empty Gemini response for VEDA.")
            parsed = self._parse_structured_response(raw_response)

            if self.config.retry_on_parse_error and "raw" in parsed:
                # Ask for correction if the LLM fails to follow format.
                correction_prompt = (
                    "Convert the following response into ONLY one valid JSON object "
                    "matching the required schema. No explanation.\n\n"
                    f"{raw_response}"
                )
                correction = self.client.models.generate_content(
                    model=self.config.model,
                    contents=correction_prompt,
                )
                raw_response = self._extract_response_text(correction) or raw_response
                parsed = self._parse_structured_response(raw_response)

            assets = await self._generate_assets(parsed, language)

            next_state = parsed.get("next_state")
            if next_state and next_state in StudentState._value2member_map_:
                context.current_state = StudentState(next_state)

            if parsed.get("confidence_update"):
                update = parsed["confidence_update"]
                concept = update.get("concept", "general")
                delta = float(update.get("delta", 0.0))
                context.update_mastery(concept, delta > 0)

            exam_question = None
            if context.current_state == StudentState.APPLY and current_chapter:
                exam_question = await self._fetch_relevant_exam_question(
                    current_chapter,
                    exam_board or self.config.exam_board_default,
                )

            context.attempts_on_current += 1

            return {
                "agent": "veda",
                "session_id": session_id,
                "state": context.current_state.value,
                "difficulty": context.difficulty.value,
                "language": language,
                "text": (parsed.get("hook", "") + "\n\n" + self._extract_conversation(raw_response)).strip(),
                "socratic_question": parsed.get("question", ""),
                "encouragement": parsed.get("encouragement", ""),
                "has_visual": bool(parsed.get("visual_needed")),
                "visual_data": assets.get("diagram"),
                "formula_html": assets.get("formula_html"),
                "formula_latex": assets.get("formula_latex"),
                "formula_engine": assets.get("formula_engine"),
                "exam_question": exam_question,
                "mastery_scores": context.concept_mastery,
                "attempts": context.attempts_on_current,
                "signals": signals,
                "tokens_used": self._extract_token_usage(response),
            }
        except Exception as exc:
            logger.exception("VEDA teach() failed: %s", exc)
            return {
                "agent": "veda",
                "error": True,
                "text": f"{vernacular.get('empathy', 'Koi nahi')}. Technical issue. Try again.",
                "fallback": True,
            }

    async def generate_revision_pdf(
        self,
        session_id: str,
        weak_areas: List[str],
        exam_board: Optional[str] = None,
    ) -> bytes:
        context = self._get_or_create_context(session_id)

        content = {
            "mastered": [k for k, v in context.concept_mastery.items() if v > 0.7],
            "weak": weak_areas,
            "formulas": await self._get_chapter_formulas(weak_areas),
            "predicted_questions": await self._get_high_probability_questions(
                weak_areas, exam_board or self.config.exam_board_default
            ),
        }

        return await self.pdf_generator.generate_revision_sheet(content)

    async def _get_high_probability_questions(
        self, chapters: List[str], board: str
    ) -> List[str]:
        questions: List[str] = []
        for chapter in chapters[:5]:
            question = await self._fetch_relevant_exam_question(chapter, board)
            if question and question.get("question_text"):
                questions.append(question["question_text"])
        return questions

    async def _get_chapter_formulas(self, chapters: List[str]) -> Dict[str, List[str]]:
        formula_db = {
            "real_numbers": [
                "Euclid: a = bq + r, 0 <= r < b",
                "HCF x LCM = product of numbers",
            ],
            "triangles": [
                "AA similarity: if two angles equal, triangles similar",
                "Pythagoras: c^2 = a^2 + b^2",
            ],
        }
        return {ch: formula_db.get(ch, []) for ch in chapters}


# ==========================================
# VEDAAdapter - Simplified interface for API endpoints
# ==========================================

class VEDAAdapter:
    """
    Simplified adapter for FastAPI endpoints
    Wraps VedaAgent with async methods expected by endpoints.py
    """

    def __init__(self):
        self.agent = VedaAgent()
        self.sessions: Dict[str, Any] = {}

    async def initialize_session(
        self,
        user_id: str,
        chapter: str,
        concept: Optional[str] = None,
        proficiency: float = 0.5,
    ):
        """Initialize new learning session"""
        session_id = f"session_{user_id}_{int(time.time())}"
        self.sessions[session_id] = {
            "user_id": user_id,
            "chapter": chapter,
            "concept": concept,
            "proficiency": proficiency,
            "questions_attempted": 0,
            "correct_streak": 0,
            "incorrect_streak": 0,
        }
        return session_id

    async def generate_feedback(
        self,
        is_correct: bool,
        question_difficulty: float,
        attempts_count: int,
        concept: str,
    ) -> Dict[str, Any]:
        """Generate feedback based on answer correctness"""
        if is_correct:
            return {
                "message": f"Correct! Well done on {concept}.",
                "hint": None,
                "type": "encouragement",
            }
        if attempts_count == 1:
            return {
                "message": f"Not quite. Think about the key properties of {concept}.",
                "hint": f"Try reviewing the formula for {concept}",
                "type": "socratic_question",
            }
        return {
            "message": f"Let's work through this. The concept of {concept} involves...",
            "hint": f"Key formula: Check the standard equation for {concept}",
            "type": "explanation",
        }

    async def adapt_difficulty(
        self, session_id: str, current_difficulty: float, is_correct: bool
    ) -> float:
        """Adjust difficulty based on performance"""
        if is_correct:
            return min(1.0, current_difficulty + 0.1)
        return max(0.1, current_difficulty - 0.1)

    async def get_recommendation(self, session_id: str) -> Dict[str, Any]:
        """Get next recommendation"""
        return {
            "action": "continue",
            "message": "Keep practicing",
            "difficulty_adjustment": 0,
        }

    async def get_hint(self, question_id: str, hint_level: int = 1) -> str:
        """Get progressive hint"""
        hints = {
            1: "Look at the given information carefully.",
            2: "Identify what you need to find.",
            3: "Apply the formula step by step.",
        }
        return hints.get(hint_level, hints[1])

