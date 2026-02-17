"""
VEDA + ORACLE Integration
The complete teaching-assessment loop
"""

from typing import Dict, List, Optional
import random
import time

# Import both systems
from ..oracle.hybrid_orchestrator import HybridOrchestrator


class VedaOracleBridge:
    """
    Connects VEDA (teacher) with ORACLE (assessor)
    Creates the adaptive learning loop:
    VEDA teaches → ORACLE tests → VEDA adapts → ORACLE retests
    """
    
    def __init__(self):
        self.orchestrator = HybridOrchestrator(ai_ratio=0.5)
        self.teaching_memory = {}  # Track what was taught to each student
        
    async def teach_concept(
        self, 
        student_id: str, 
        concept: str,
        explanation_depth: str = "standard"
    ) -> Dict:
        """
        VEDA teaches a concept, then ORACLE provides practice
        """
        # 1. VEDA generates explanation (mock for now)
        explanation = self._generate_explanation(concept, explanation_depth)
        
        # 2. ORACLE generates immediate practice question
        practice_question = self.orchestrator.generate_question(
            concept=concept,
            marks=2,  # Start easy
            difficulty=0.4,
            student_id=student_id
        )
        
        # 3. Store teaching context
        self.teaching_memory[student_id] = {
            "concept": concept,
            "explanation": explanation,
            "practice_question_id": practice_question.question_id,
            "attempts": 0,
            "correct_streak": 0
        }
        
        return {
            "lesson": explanation,
            "practice_question": {
                "id": practice_question.question_id,
                "text": practice_question.question_text,
                "visual": practice_question.jsxgraph_code,
                "hints": practice_question.socratic_hints,
                "difficulty": practice_question.difficulty
            },
            "next_action": "attempt_practice"
        }
    
    async def process_attempt(
        self,
        student_id: str,
        question_id: str,
        student_answer: str,
        time_taken: int,
        hints_used: int = 0
    ) -> Dict:
        """
        Process student answer and adapt next step
        """
        # Get teaching context
        context = self.teaching_memory.get(student_id, {})
        concept = context.get("concept", "general")
        
        # Mock verification (in real app, compare with stored answer)
        is_correct = self._verify_answer(student_answer, question_id)
        
        # Update tracking
        context["attempts"] += 1
        if is_correct:
            context["correct_streak"] += 1
        else:
            context["correct_streak"] = 0
        
        # Decision logic: What next?
        if is_correct and context["correct_streak"] >= 2:
            # Student mastered - advance difficulty
            next_difficulty = min(1.0, context.get("difficulty", 0.4) + 0.2)
            next_marks = min(5, context.get("marks", 2) + 1)
            
            next_q = self.orchestrator.generate_question(
                concept=concept,
                marks=next_marks,
                difficulty=next_difficulty,
                student_id=student_id
            )
            
            return {
                "result": "correct",
                "feedback": "🎉 Excellent! You've mastered this. Let's try something harder.",
                "next_question": {
                    "id": next_q.question_id,
                    "text": next_q.question_text,
                    "difficulty": next_q.difficulty,
                    "source": next_q.source  # "pattern" or "ai"
                },
                "concept_status": "advancing"
            }
            
        elif is_correct and context["correct_streak"] == 1:
            # One correct - need more practice
            next_q = self.orchestrator.generate_question(
                concept=concept,
                marks=2,
                difficulty=0.5,
                student_id=student_id
            )
            
            return {
                "result": "correct",
                "feedback": "✅ Good! One more like this to be sure.",
                "next_question": {
                    "id": next_q.question_id,
                    "text": next_q.question_text
                },
                "concept_status": "practicing"
            }
            
        elif not is_correct and context["attempts"] >= 3:
            # Multiple failures - VEDA reteaches
            return {
                "result": "incorrect",
                "feedback": "🤔 This is tricky. Let me explain it differently...",
                "next_action": "reteach",
                "hint_level": 3,  # Give full hint
                "alternative_explanation": self._generate_alternative_explanation(concept),
                "concept_status": "struggling"
            }
            
        else:
            # First failure - give hint and similar question
            next_q = self.orchestrator.generate_question(
                concept=concept,
                marks=2,
                difficulty=0.4,  # Slightly easier
                force_source="pattern",  # Use reliable pattern
                student_id=student_id
            )
            
            return {
                "result": "incorrect",
                "feedback": "❌ Not quite. Here's a hint...",
                "hint": self._get_hint_for_question(question_id, level=2),
                "next_question": {
                    "id": next_q.question_id,
                    "text": next_q.question_text
                },
                "concept_status": "reviewing"
            }
    
    async def generate_adaptive_exam(
        self,
        student_id: str,
        chapters: List[int],
        weak_areas_only: bool = False
    ) -> Dict:
        """
        Generate personalized exam based on student's weak areas
        Uses 50-50 split but prioritizes weak concepts
        """
        # Get student's skill profile (mock - in real app, query DB)
        weak_concepts = self._identify_weak_areas(student_id) if weak_areas_only else []
        
        questions = []
        question_distribution = {
            1: 18,  # MCQ/VSA
            2: 5,   # VSA
            3: 6,   # SA
            4: 3,   # Case study
            5: 4    # LA
        }
        
        for marks, count in question_distribution.items():
            for i in range(count):
                # Alternate sources for variety
                force_source = "ai" if i % 2 == 0 else "pattern"
                
                # Select concept (prioritize weak areas)
                if weak_concepts and i < count // 2:
                    concept = random.choice(weak_concepts)
                else:
                    concept = self._select_concept_from_chapters(chapters)
                
                q = self.orchestrator.generate_question(
                    concept=concept,
                    marks=marks,
                    difficulty=self._marks_to_difficulty(marks),
                    force_source=force_source,
                    student_id=student_id
                )
                
                questions.append({
                    "question_id": q.question_id,
                    "section": self._get_section_for_marks(marks),
                    "marks": marks,
                    "concept": concept,
                    "source": q.source,
                    "text": q.question_text,
                    "visual": q.jsxgraph_code
                })
        
        return {
            "exam_id": f"EXAM_{student_id}_{int(time.time())}",
            "questions": questions,
            "total_questions": len(questions),
            "total_marks": sum(q["marks"] for q in questions),
            "ai_percentage": len([q for q in questions if q["source"] == "ai"]) / len(questions) * 100,
            "focus": "weak_areas" if weak_areas_only else "comprehensive"
        }
    
    def _generate_explanation(self, concept: str, depth: str) -> str:
        """VEDA generates teaching explanation"""
        explanations = {
            "trigonometry_heights": {
                "basic": "Trigonometry helps us find heights without climbing! We use the angle of elevation...",
                "standard": "When you look up at a building, the angle between your eye level and the top is called angle of elevation. Using tan θ = height/distance, we can calculate...",
                "detailed": "The key insight is that the observer, the base of the object, and the top form a right triangle. We know the distance (adjacent) and angle, so tan θ = opposite/adjacent = height/distance..."
            },
            "quadratic_equations": {
                "standard": "A quadratic equation has the form ax² + bx + c = 0. We can solve it using factorization, completing the square, or the quadratic formula..."
            }
        }
        return explanations.get(concept, {}).get(depth, f"Let me explain {concept}...")
    
    def _generate_alternative_explanation(self, concept: str) -> str:
        """Different approach for struggling students"""
        alternatives = {
            "trigonometry_heights": "Imagine you have a ladder leaning against a wall. The angle it makes with the ground tells you how steep it is. If you know the angle and how far the ladder is from the wall, you can find how high it reaches using tan(angle) = height / distance",
            "quadratic_equations": "Think of a quadratic as a parabola. The roots are where it crosses the x-axis. If it touches at one point, roots are equal. If it doesn't cross, no real roots..."
        }
        return alternatives.get(concept, "Let me try a different approach...")
    
    def _verify_answer(self, student_answer: str, question_id: str) -> bool:
        """Mock verification - real app would query DB"""
        # Mock: 70% accuracy for demo
        return random.random() > 0.3
    
    def _get_hint_for_question(self, question_id: str, level: int) -> str:
        """Retrieve appropriate hint"""
        hints = [
            "What formula relates the given values?",
            "Think about the trigonometric ratio: sin, cos, or tan?",
            "Substitute the values into tan θ = opposite/adjacent"
        ]
        return hints[level-1] if level <= len(hints) else "Review the concept"
    
    def _identify_weak_areas(self, student_id: str) -> List[str]:
        """Mock - real app would query skill_mastery table"""
        return ["trigonometry_heights", "quadratic_nature"]
    
    def _select_concept_from_chapters(self, chapters: List[int]) -> str:
        """Select random concept from given chapters"""
        concept_map = {
            4: ["quadratic_equations", "quadratic_nature", "quadratic_formula"],
            5: ["arithmetic_progression", "ap_sum", "ap_nth_term"],
            8: ["trigonometry_heights", "trigonometry_distances", "trigonometry_identities"],
            10: ["circles_tangent", "circles_chord"]
        }
        available = []
        for ch in chapters:
            available.extend(concept_map.get(ch, []))
        return random.choice(available) if available else "general"
    
    def _marks_to_difficulty(self, marks: int) -> float:
        return {1: 0.3, 2: 0.45, 3: 0.6, 4: 0.7, 5: 0.8}.get(marks, 0.5)
    
    def _get_section_for_marks(self, marks: int) -> str:
        return {1: "A", 2: "B", 3: "C", 4: "D", 5: "E"}.get(marks, "C")


# Usage example for main app
class LokaahLearningSession:
    """
    Main class for a student learning session
    Combines VEDA teaching + ORACLE assessment
    """
    
    def __init__(self, student_id: str):
        self.student_id = student_id
        self.bridge = VedaOracleBridge()
        self.session_history = []
    
    async def start_lesson(self, concept: str):
        """Begin teaching a concept"""
        result = await self.bridge.teach_concept(
            student_id=self.student_id,
            concept=concept
        )
        return result
    
    async def submit_answer(self, question_id: str, answer: str, time_taken: int):
        """Process student answer"""
        result = await self.bridge.process_attempt(
            student_id=self.student_id,
            question_id=question_id,
            student_answer=answer,
            time_taken=time_taken
        )
        self.session_history.append(result)
        return result
    
    async def take_exam(self, chapters: List[int]):
        """Generate personalized exam"""
        return await self.bridge.generate_adaptive_exam(
            student_id=self.student_id,
            chapters=chapters,
            weak_areas_only=False
        )
