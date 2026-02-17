"""
AI-Powered ORACLE for CBSE Class 10 Mathematics
100% AI generation - NO hardcoding
Gemini-based question generation
"""

import os
import json
import random
from google import genai
import math
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import anthropic  # type: ignore
except Exception:  # pragma: no cover - legacy path only
    class _AnthropicStub:
        class BadRequestError(Exception):
            pass

    anthropic = _AnthropicStub()  # type: ignore


@dataclass
class CBSEChapterSpec:
    """CBSE Class 10 Mathematics Chapter Specification"""
    number: int
    name: str
    marks_weightage: int
    topics: List[str]
    exam_patterns: List[str]
    question_style: str
    common_mistakes: List[str]


class CBSEClass10MathOracle:
    """
    AI-Powered Question Generator for CBSE Class 10 Mathematics ONLY
    Generates infinite unique questions using Gemini
    """
    
    def __init__(self):
        # Gemini-only runtime path.
        self.claude = None

        self.gemini_client = None
        gemini_key = os.getenv("GEMINI_API_KEY")
        try:
            if gemini_key:
                self.gemini_client = genai.Client(api_key=gemini_key)
            else:
                raise ValueError("GEMINI_API_KEY not set.")
        except Exception as e:
            print(f"Gemini initialization failed: {e}")

        if not self.gemini_client:
            raise ValueError(
                "Gemini not available. Set GEMINI_API_KEY or GOOGLE_APPLICATION_CREDENTIALS."
            )
        
        # CBSE Class 10 Mathematics Complete Specification (2025-26)
        self.chapters = {
            1: CBSEChapterSpec(
                number=1,
                name="Real Numbers",
                marks_weightage=6,
                topics=[
                    "Euclid's Division Lemma",
                    "Fundamental Theorem of Arithmetic",
                    "HCF and LCM by prime factorization",
                    "Terminating and non-terminating decimals",
                    "Irrationality proofs (√2, √3, √5)"
                ],
                exam_patterns=[
                    "Prove √p is irrational (3 marks, 9/11 papers)",
                    "Decimal expansion terminates or not (1 mark, 11/11 papers)",
                    "HCF-LCM relationship verification (2 marks, 8/11 papers)",
                    "Euclid's division lemma application (2 marks, 6/11 papers)"
                ],
                question_style="Theoretical proofs using contradiction OR numerical HCF/LCM calculations",
                common_mistakes=[
                    "Not assuming √p is rational at start of proof",
                    "Forgetting to state 'contradiction' in irrationality proofs",
                    "Incorrect prime factorization"
                ]
            ),
            2: CBSEChapterSpec(
                number=2,
                name="Polynomials",
                marks_weightage=7,
                topics=[
                    "Zeroes of polynomial",
                    "Relationship: α+β = -b/a, αβ = c/a",
                    "Division algorithm for polynomials",
                    "Quadratic polynomials and their graphs"
                ],
                exam_patterns=[
                    "Find zeroes and verify sum/product (2 marks, 10/11 papers)",
                    "Form polynomial from given zeroes (2 marks, 7/11 papers)",
                    "Verify division algorithm (3 marks, 6/11 papers)",
                    "Find k if (x-a) is a factor (2 marks, 5/11 papers)"
                ],
                question_style="Verify relationships OR form polynomials from conditions OR division algorithm",
                common_mistakes=[
                    "Wrong signs in sum of zeroes formula",
                    "Not simplifying polynomial after formation",
                    "Division algorithm: dividend ≠ divisor × quotient + remainder"
                ]
            ),
            8: CBSEChapterSpec(
                number=8,
                name="Introduction to Trigonometry",
                marks_weightage=12,
                topics=[
                    "Trigonometric ratios: sin, cos, tan, cosec, sec, cot",
                    "Values at 0°, 30°, 45°, 60°, 90°",
                    "Complementary angles: sin(90°-θ) = cos θ",
                    "Trigonometric identities: sin²θ + cos²θ = 1, etc.",
                    "Heights and distances applications"
                ],
                exam_patterns=[
                    "Heights and distances (3 marks, 9/11 papers)",
                    "Two angles from same object (5 marks, 7/11 papers)",
                    "Trigonometric identity proof (3 marks, 9/11 papers)",
                    "Shadow/ladder problems (2 marks, 6/11 papers)"
                ],
                question_style="Heights-distances with tan/sin/cos OR prove identities using basic identities",
                common_mistakes=[
                    "Angle of elevation vs angle of depression confusion",
                    "Not using correct trigonometric ratio (opposite/adjacent/hypotenuse)",
                    "Identity proofs: not converting to sin and cos"
                ]
            ),
            15: CBSEChapterSpec(
                number=15,
                name="Probability",
                marks_weightage=5,
                topics=[
                    "Classical probability: P(E) = n(E)/n(S)",
                    "Complementary events: P(not E) = 1 - P(E)",
                    "Probability with playing cards",
                    "Probability with dice",
                    "Probability with balls/coins"
                ],
                exam_patterns=[
                    "Single card probability (1 mark, 9/11 papers)",
                    "Two events probability (2 marks, 8/11 papers)",
                    "Dice problems (2 marks, 7/11 papers)",
                    "Balls without replacement (3 marks, 6/11 papers)"
                ],
                question_style="Calculate probability as favorable/total outcomes",
                common_mistakes=[
                    "Not reducing fraction to simplest form",
                    "With/without replacement confusion",
                    "Probability > 1 or < 0"
                ]
            )
        }
        
        # Indian contexts for CBSE questions
        self.indian_contexts = {
            "monuments": [
                "India Gate (Delhi)", "Qutub Minar (Delhi)", "Gateway of India (Mumbai)",
                "Red Fort (Delhi)", "Taj Mahal (Agra)", "Charminar (Hyderabad)",
                "Mysore Palace", "Victoria Memorial (Kolkata)", "Hawa Mahal (Jaipur)"
            ],
            "daily_life": [
                "Kite flying during Makar Sankranti", "Cricket match in local ground",
                "Vegetable market shopping", "Temple darshan", "Diwali decoration",
                "Republic Day parade", "Garba dance during Navratri", "Morning yoga session"
            ],
            "transport": [
                "Delhi Metro", "Mumbai Local train", "Auto-rickshaw ride",
                "City bus", "Cycle rickshaw", "Ola/Uber cab"
            ],
            "education": [
                "School assembly", "Classroom seating arrangement", "Library books",
                "Exam hall", "Science lab experiment", "Sports day event"
            ],
            "names": {
                "male": ["Rahul", "Amit", "Rohan", "Arjun", "Karan", "Aditya", "Vikram", "Sanjay"],
                "female": ["Priya", "Neha", "Anjali", "Sneha", "Kavya", "Riya", "Pooja", "Divya"]
            }
        }
        
        print("✅ CBSE Class 10 Math AI Oracle initialized")
        print(f"   - {len(self.chapters)} chapters configured")
        if self.claude:
            print("   - Claude Sonnet 4.5 ready (primary)")
        if self.gemini_client:
            print("   - Gemini 2.5 Flash ready (fallback)")
        if not self.claude and self.gemini_client:
            print("   - Using Gemini 2.5 Flash as primary provider")
    
    def generate_question(
        self,
        chapter_number: int,
        marks: int,
        difficulty: float = None
    ) -> Dict:
        """
        Generate unique CBSE Class 10 Math question using AI
        
        Args:
            chapter_number: 1-15 (CBSE chapters, excluding 9)
            marks: 1, 2, 3, 4, or 5
            difficulty: 0.0-1.0 (auto-calculated from marks if not provided)
        
        Returns:
            Complete CBSE-formatted question with solution and hints
        """
        
        # Validate chapter
        if chapter_number not in self.chapters:
            raise ValueError(f"Invalid chapter number: {chapter_number}. Available: 1, 2, 8, 15")
        
        chapter = self.chapters[chapter_number]
        
        # Auto-calculate difficulty from marks if not provided
        if difficulty is None:
            difficulty = self._marks_to_difficulty(marks)
        
        # Select random Indian context
        context = self._select_indian_context()
        
        print(f"\n🤖 Generating CBSE Class 10 Math question...")
        print(f"   Chapter {chapter_number}: {chapter.name}")
        print(f"   Marks: {marks}, Difficulty: {difficulty}")
        print(f"   Context: {context['setting']}")
        
        # Build CBSE-specific prompt
        prompt = self._build_cbse_prompt(chapter, marks, difficulty, context)
        
        # Call AI API (with fallback)
        response_text = None
        provider_used = None
        
        try:
            # Try Anthropic Claude first (if available and has credits)
            if self.claude:
                try:
                    response = self.claude.messages.create(
                        model="claude-sonnet-4-20250514",  # Latest Sonnet 4
                        max_tokens=3500,
                        temperature=0.9,  # High creativity for unique scenarios
                        messages=[{"role": "user", "content": prompt}]
                    )
                    response_text = response.content[0].text.strip()
                    provider_used = "Claude Sonnet 4.5"
                    print(f"   ✓ Generated using Claude Sonnet 4.5")
                
                except anthropic.BadRequestError as e:
                    # API key issue or credit balance low
                    if "credit balance" in str(e).lower():
                        print(f"   ⚠️  Claude credits exhausted, falling back to Gemini...")
                        if not self.gemini_client:
                            raise ValueError("Claude credits exhausted and Gemini not available")
                    else:
                        raise
            
            # Fallback to Gemini if Claude not available or failed
            if not response_text and self.gemini_client:
                response = self.gemini_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        temperature=0.9,
                        max_output_tokens=3500
                    )
                )
                response_text = response.text.strip()
                provider_used = "Gemini 2.5 Flash"
                print(f"   ✓ Generated using Gemini 2.5 Flash")
            
            # If still no response
            if not response_text:
                raise ValueError("No AI provider could generate a response")
            
            # Parse response
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif response_text.startswith("```"):
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            question = json.loads(response_text)
            
            # Add metadata
            question['question_id'] = self._generate_question_id(chapter_number, marks)
            question['chapter_number'] = chapter_number
            question['chapter_name'] = chapter.name
            question['marks'] = marks
            question['difficulty'] = difficulty
            question['generation_method'] = 'ai_powered'
            question['ai_provider'] = provider_used
            question['generated_at'] = datetime.now().isoformat()
            question['context_used'] = context
            
            print(f"   ✅ Question generated successfully")
            
            # Validate
            validator = CBSEClass10MathValidator()
            is_valid, validation_msg = validator.validate_question(question, chapter_number)
            
            if not is_valid:
                print(f"   ⚠️ Validation warning: {validation_msg}")
            
            return question
            
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON parsing error: {e}")
            print(f"   Response text: {response_text[:500]}")
            raise
        except Exception as e:
            print(f"   ❌ Generation error: {e}")
            raise
    
    def _build_cbse_prompt(
        self,
        chapter: CBSEChapterSpec,
        marks: int,
        difficulty: float,
        context: Dict
    ) -> str:
        """
        Build CBSE Class 10 specific prompt for Claude
        """
        
        # Determine question type from marks
        question_types = {
            1: "MCQ or Very Short Answer (VSA)",
            2: "Very Short Answer (VSA)",
            3: "Short Answer (SA)",
            4: "Case Study sub-part",
            5: "Long Answer (LA)"
        }
        
        question_type = question_types.get(marks, "SA")
        
        # Select topic from chapter
        topic = random.choice(chapter.topics)
        
        # Select exam pattern example
        exam_pattern = random.choice(chapter.exam_patterns)
        
        prompt = f"""You are an expert CBSE Class 10 Mathematics question paper creator with deep knowledge of CBSE exam patterns from 2015-2025.

Generate a COMPLETELY UNIQUE question for:

**CBSE Class 10 Mathematics (2025-26 Syllabus)**
**Chapter {chapter.number}: {chapter.name}** (Weightage: {chapter.marks_weightage} marks)
**Topic: {topic}**
**Question Type: {question_type}**
**Marks: {marks}**
**Difficulty: {difficulty:.1f}/1.0**

**CRITICAL REQUIREMENTS:**

1. **CBSE Exam Pattern Compliance:**
   Reference: "{exam_pattern}"
   Question style: {chapter.question_style}

2. **Use This Indian Context:**
   - Setting: {context['setting']}
   - Character name: {context['character']} ({context['gender']})
   - Additional element: {context['element']}

3. **CBSE Language Standards:**
   - Start with: "Find", "Prove", "Verify", "Calculate", "Show that", "Determine"
   - Use CBSE terminology exactly as in past papers
   - Include "Use √3 = 1.73" or "Use π = 22/7" when applicable
   - For 3+ marks: "Show your work" or "Justify your answer"

4. **Unique Scenario Creation:**
   - This must be a NEW scenario never used before
   - Use varied, realistic numbers that give clean answers
   - Avoid common textbook examples
   - Make it engaging and relatable for 15-year-old Indian students

5. **Step-by-Step Solution:**
   - Exactly {marks} main steps (one per mark)
   - Each step should be clear and complete
   - Final answer must have correct units
   - Follow CBSE marking scheme pattern

6. **Common Mistakes to Avoid:**
{chr(10).join(['   - ' + mistake for mistake in chapter.common_mistakes])}

7. **Mathematical Accuracy:**
   - Ensure all calculations are correct
   - Use appropriate formulas from CBSE syllabus
   - Verify final answer before outputting

**OUTPUT FORMAT (STRICT JSON):**

{{
    "question_text": "Complete CBSE-style question using the Indian context provided. Be specific and clear.",
    
    "given_data": {{
        "list all values given in the question as key-value pairs"
    }},
    
    "to_find": "Clearly state what needs to be calculated or proved",
    
    "solution_steps": [
        "Step 1: [1 mark] Describe what this step does",
        "Step 2: [1 mark] Describe calculation/reasoning",
        ...{marks} steps total
    ],
    
    "final_answer": "Complete answer with appropriate units",
    
    "marking_scheme": {{
        "step_1": "1 mark for [specific thing]",
        "step_2": "1 mark for [specific thing]",
        ...{marks} entries total
    }},
    
    "socratic_hints": [
        {{
            "level": 1,
            "hint": "Gentle nudge - what concept applies?",
            "nudge": "Think about which chapter topic this relates to"
        }},
        {{
            "level": 2,
            "hint": "More specific - which formula?",
            "nudge": "Recall the formula for..."
        }},
        {{
            "level": 3,
            "hint": "Almost complete - how to apply?",
            "nudge": "Substitute the values into the formula"
        }}
    ],
    
    "cbse_metadata": {{
        "chapter": "{chapter.name}",
        "topic": "{topic}",
        "question_type": "{question_type}",
        "similar_to": "Year and question number from past papers (e.g., '2024 Q15')",
        "difficulty_level": "Easy/Medium/Hard"
    }},
    
    "calculations_check": {{
        "formula_used": "Write the main formula(s) used",
        "values_substituted": {{}},
        "intermediate_results": [],
        "final_result": "numeric value"
    }}
}}

**CRITICAL:** 
- This MUST look exactly like a CBSE Class 10 Mathematics question from 2015-2025 board exams
- Generate UNIQUE numbers and scenario - do not repeat common textbook examples
- Ensure mathematical correctness - verify all calculations
- Use natural, student-friendly language while maintaining CBSE formality

Return ONLY the JSON object, no additional text."""

        return prompt
    
    def _select_indian_context(self) -> Dict:
        """
        Select random Indian context for question
        """
        context_types = list(self.indian_contexts.keys())
        context_type = random.choice([t for t in context_types if t != 'names'])
        
        setting = random.choice(self.indian_contexts[context_type])
        gender = random.choice(['male', 'female'])
        character = random.choice(self.indian_contexts['names'][gender])
        
        # Additional element for variety
        other_type = random.choice([t for t in context_types if t not in ['names', context_type]])
        element = random.choice(self.indian_contexts[other_type])
        
        return {
            'type': context_type,
            'setting': setting,
            'character': character,
            'gender': gender,
            'element': element
        }
    
    def _marks_to_difficulty(self, marks: int) -> float:
        """
        Convert marks to difficulty score
        """
        difficulty_map = {
            1: 0.3,   # Easy
            2: 0.45,  # Medium-Easy
            3: 0.6,   # Medium
            4: 0.7,   # Medium-Hard
            5: 0.8    # Hard
        }
        return difficulty_map.get(marks, 0.5)
    
    def _generate_question_id(self, chapter: int, marks: int) -> str:
        """
        Generate unique question ID
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        return f"CBSE10_AI_CH{chapter:02d}_M{marks}_{timestamp}"


class CBSEClass10MathValidator:
    """
    Validates AI-generated CBSE Class 10 Math questions
    """
    
    def validate_question(self, question: Dict, chapter_number: int) -> tuple:
        """
        Validate question meets CBSE standards
        
        Returns:
            (is_valid, message)
        """
        
        # Check 1: Required fields present
        required_fields = [
            'question_text', 'solution_steps', 'final_answer',
            'marking_scheme', 'socratic_hints', 'cbse_metadata'
        ]
        
        missing_fields = [f for f in required_fields if f not in question]
        if missing_fields:
            return False, f"Missing required fields: {missing_fields}"
        
        # Check 2: Solution steps match marks
        marks = question.get('marks', len(question['solution_steps']))
        if len(question['solution_steps']) < marks:
            return False, f"Insufficient solution steps: got {len(question['solution_steps'])}, need {marks}"
        
        # Check 3: CBSE language compliance
        question_lower = question['question_text'].lower()
        cbse_keywords = ['find', 'prove', 'verify', 'calculate', 'show', 'determine']
        if not any(keyword in question_lower for keyword in cbse_keywords):
            return False, "Question doesn't use CBSE command words (find/prove/verify/etc.)"
        
        # All checks passed
        return True, "Valid CBSE Class 10 Math question"


# Test function
def test_ai_oracle():
    """
    Test the AI-powered ORACLE with sample questions
    """
    print("=" * 70)
    print("TESTING CBSE CLASS 10 MATH AI ORACLE")
    print("=" * 70)
    
    oracle = CBSEClass10MathOracle()
    
    # Test cases: different chapters and marks
    test_cases = [
        {"chapter": 1, "marks": 3, "name": "Real Numbers - Irrationality Proof"},
        {"chapter": 8, "marks": 3, "name": "Trigonometry - Heights & Distances"},
        {"chapter": 15, "marks": 2, "name": "Probability - Cards"},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}: {test_case['name']}")
        print(f"{'='*70}")
        
        try:
            question = oracle.generate_question(
                chapter_number=test_case['chapter'],
                marks=test_case['marks']
            )
            
            # Display question
            print(f"\n📝 QUESTION:")
            print(f"{question['question_text']}\n")
            
            print(f"✅ FINAL ANSWER:")
            print(f"{question['final_answer']}\n")
            
            print(f"📊 METADATA:")
            print(f"   Question ID: {question['question_id']}")
            print(f"   Chapter: {question['chapter_name']}")
            print(f"   Marks: {question['marks']}")
            print(f"   Difficulty: {question['difficulty']}")
            print(f"   Context: {question['context_used']['setting']}")
            
            print(f"\n✅ Test {i} PASSED")
            
        except Exception as e:
            print(f"\n❌ Test {i} FAILED: {e}")
    
    print(f"\n{'='*70}")
    print("AI ORACLE TESTING COMPLETE")
    print(f"{'='*70}")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ERROR: ANTHROPIC_API_KEY not found in environment")
        print("   Please set it in your .env file")
    else:
        test_ai_oracle()
