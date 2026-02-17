"""
QUICK REFERENCE: Hybrid Oracle Usage
Copy-paste code snippets for common tasks
"""

# ============================================================================
# 1. GENERATE SINGLE QUESTION (Pattern or AI, Auto-Decided)
# ============================================================================

from app.oracle.hybrid_orchestrator import get_hybrid_orchestrator

orchestrator = get_hybrid_orchestrator(ai_ratio=0.5)  # 50-50 split

question = orchestrator.generate_question(
    concept="trigonometry_heights",
    marks=3,
    difficulty=0.6
)

print(f"Source: {question.source}")  # "pattern" or "ai"
print(f"Question: {question.question_text}")
print(f"Answer: {question.final_answer}")
print(f"Hints: {question.socratic_hints}")
if question.jsxgraph_code:
    print(f"Visual: {question.jsxgraph_code[:100]}...")


# ============================================================================
# 2. FORCE SPECIFIC SOURCE (Pattern or AI)
# ============================================================================

# Force Pattern ORACLE (fast, reliable, free)
pattern_q = orchestrator.generate_question(
    concept="quadratic_nature_of_roots",
    marks=2,
    difficulty=0.5,
    force_source="pattern"
)

# Force AI ORACLE (creative, unique, costs $0.003)
ai_q = orchestrator.generate_question(
    concept="trigonometry_heights",
    marks=3,
    difficulty=0.6,
    force_source="ai"
)


# ============================================================================
# 3. GENERATE COMPLETE EXAM (50-50 Mix)
# ============================================================================

exam = orchestrator.generate_exam(
    chapters=[4, 5, 8, 10],  # Quadratic, AP, Trig, Circles
    total_marks=80,
    duration_minutes=180
)

print(f"Exam ID: {exam['exam_id']}")
print(f"Total Questions: {len(exam['questions'])}")
print(f"AI Questions: {exam['ai_percentage']}%")
print(f"Pattern Questions: {exam['pattern_percentage']}%")

for q in exam['questions'][:3]:  # First 3 questions
    print(f"\n[{q['source'].upper()}] {q['question_text'][:60]}...")


# ============================================================================
# 4. VEDA + ORACLE LEARNING LOOP (Adaptive Teaching)
# ============================================================================

from app.veda.oracle_integration import LokaahLearningSession
import asyncio

async def teaching_session():
    session = LokaahLearningSession(student_id="student_123")
    
    # Step 1: Teach concept + generate practice question
    lesson = await session.start_lesson("trigonometry_heights")
    print(f"Lesson: {lesson['lesson']}")
    print(f"Practice: {lesson['practice_question']['text']}")
    
    # Step 2: Student attempts question
    result = await session.submit_answer(
        question_id=lesson['practice_question']['id'],
        answer="43.30m",
        time_taken=120
    )
    
    print(f"Feedback: {result['feedback']}")
    print(f"Status: {result['concept_status']}")
    
    if result['result'] == 'correct':
        # Student got it right - next harder question
        print(f"Next: {result['next_question']['text']}")
    else:
        # Student struggling - reteach with alternative explanation
        print(f"Hint: {result['hint']}")

# Run async function
asyncio.run(teaching_session())


# ============================================================================
# 5. API USAGE (REST Endpoints)
# ============================================================================

import requests

# Generate question via API
response = requests.post(
    "http://localhost:8000/api/v1/question/generate",
    json={
        "concept": "arithmetic_progression",
        "marks": 3,
        "difficulty": 0.6,
        "force_source": None  # Auto-decide
    }
)

question_data = response.json()
print(f"Question ID: {question_data['question_id']}")
print(f"Source: {question_data['source']}")
print(f"Question: {question_data['question_text']}")
print(f"Answer: {question_data['final_answer']}")

# Generate exam via API
exam_response = requests.post(
    "http://localhost:8000/api/v1/exam/generate",
    json={
        "chapters": [4, 5, 8],
        "total_marks": 80,
        "duration_minutes": 180
    }
)

exam_data = exam_response.json()
print(f"Exam ID: {exam_data['exam_id']}")
print(f"Questions: {len(exam_data['questions'])}")

# Get stats
stats = requests.get("http://localhost:8000/api/v1/stats").json()
print(f"Total Generated: {stats['total_generated']}")
print(f"Cost Estimate: ${stats['ai_engine_stats']['estimated_api_cost_usd']}")


# ============================================================================
# 6. WEBSOCKET REAL-TIME PRACTICE
# ============================================================================

import asyncio
import websockets
import json

async def practice_session():
    uri = "ws://localhost:8000/api/v1/ws/practice"
    async with websockets.connect(uri) as websocket:
        # Request question
        await websocket.send(json.dumps({
            "action": "get_question",
            "concept": "trigonometry_heights",
            "difficulty": 0.6
        }))
        
        # Receive question
        response = await websocket.recv()
        data = json.loads(response)
        
        if data['type'] == 'question':
            print(f"Question: {data['data']['text']}")
            print(f"Source: {data['data']['source']}")
            
            # Submit answer
            await websocket.send(json.dumps({
                "action": "submit_answer",
                "answer": "43.30m",
                "expected_answer": "43.30m",
                "concept": "trigonometry_heights"
            }))
            
            # Receive feedback
            feedback = await websocket.recv()
            feedback_data = json.loads(feedback)
            print(f"Correct: {feedback_data['correct']}")

asyncio.run(practice_session())


# ============================================================================
# 7. COST TRACKING
# ============================================================================

# Get detailed statistics
stats = orchestrator.get_stats()

print(f"Total Questions: {stats['total_generated']}")
print(f"Pattern Questions: {stats['pattern_count']} (Free)")
print(f"AI Questions: {stats['ai_count']} (Paid)")
print(f"Average Time: {stats['avg_generation_time_ms']:.1f}ms")

# AI Engine specific stats
ai_stats = stats['ai_engine_stats']
print(f"Estimated Cost: ${ai_stats['estimated_api_cost_usd']}")
print(f"Claude Available: {ai_stats['claude_available']}")
print(f"Gemini Available: {ai_stats['gemini_available']}")


# ============================================================================
# 8. CUSTOM AI RATIO (Adjust Pattern vs AI Split)
# ============================================================================

# 70% Pattern, 30% AI (cheaper, faster)
cost_optimized = get_hybrid_orchestrator(ai_ratio=0.3)

# 30% Pattern, 70% AI (more creative, unique)
creativity_focused = get_hybrid_orchestrator(ai_ratio=0.7)

# 100% Pattern (free, fastest, but limited variety)
pattern_only = get_hybrid_orchestrator(ai_ratio=0.0)

# 100% AI (most creative, but expensive)
ai_only = get_hybrid_orchestrator(ai_ratio=1.0)


# ============================================================================
# 9. CONCEPT LIST
# ============================================================================

AVAILABLE_CONCEPTS = [
    # Trigonometry
    "trigonometry_heights",
    "trigonometry_distances",
    
    # Quadratic Equations
    "quadratic_nature_of_roots",
    "quadratic_formula_solve",
    "quadratic_roots",
    "quadratic_consecutive_integers",
    "quadratic_age_problem",
    "quadratic_area_perimeter",
    
    # Arithmetic Progressions
    "arithmetic_progression",
    "ap_nth_term_basic",
    "ap_sum_n_terms",
    "ap_find_common_difference",
    "ap_salary_increment",
    "ap_auditorium_seats",
    
    # Probability
    "probability_basic",
    "probability_single_card",
    "probability_two_dice",
    "probability_balls_without_replacement",
    
    # Circles
    "circles_tangent",
    
    # Coordinate Geometry
    "coordinate_distance",
    "coordinate_section",
    
    # Triangles
    "triangles_similarity",
    
    # Mensuration
    "mensuration_sector",
    
    # Statistics
    "statistics_mean",
]


# ============================================================================
# 10. TROUBLESHOOTING
# ============================================================================

# Check if AI providers are working
from app.oracle.true_ai_oracle import TrueAIOracle

oracle = TrueAIOracle()
print(f"Claude Available: {oracle.claude is not None}")
print(f"Gemini Available: {oracle.gemini is not None}")

# If both are None, check .env file for API keys
import os
print(f"ANTHROPIC_API_KEY set: {bool(os.getenv('ANTHROPIC_API_KEY'))}")
print(f"GEMINI_API_KEY set: {bool(os.getenv('GEMINI_API_KEY'))}")

# Test generation (will fallback to Gemini if Claude fails)
try:
    test_q = oracle.generate_question(
        concept="trigonometry_heights",
        marks=3,
        difficulty=0.5
    )
    print(f"✅ Generation working! Question: {test_q.question_text[:50]}...")
except Exception as e:
    print(f"❌ Generation failed: {e}")


# ============================================================================
# PRODUCTION TIPS
# ============================================================================

"""
1. Cost Optimization:
   - Use 70% pattern, 30% AI for daily practice (ai_ratio=0.3)
   - Use 50-50 for exams (balanced)
   - Use 100% pattern for free tier users

2. Performance:
   - Pattern questions: 10-50ms (instant)
   - AI questions: 500-2000ms (cache if possible)
   - Pre-generate popular questions during off-peak

3. Quality Assurance:
   - AI generates scenario ONLY (not math)
   - Python always calculates (100% accurate)
   - Validate AI JSON output before calculation

4. User Experience:
   - Show "source" to students? (optional transparency)
   - Use AI for "surprise questions" feature
   - Use patterns for "practice mode"

5. Monitoring:
   - Track API costs daily
   - Monitor generation success rate
   - Log failed generations for debugging
   - Alert if cost > threshold
"""
