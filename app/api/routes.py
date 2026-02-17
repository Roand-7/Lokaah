"""
FASTAPI ROUTES - Hybrid ORACLE Integration
Exposes question generation, exam creation, and teaching endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, WebSocket
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import time
import random

# Import hybrid orchestrator
from ..oracle.hybrid_orchestrator import get_hybrid_orchestrator

# Router
router = APIRouter(prefix="/api/v1", tags=["oracle"])

# Pydantic Models
class QuestionRequest(BaseModel):
    concept: str
    marks: int = 3
    difficulty: float = 0.5
    student_id: Optional[str] = None
    force_source: Optional[str] = None  # "pattern", "ai", or None for auto

class QuestionResponse(BaseModel):
    question_id: str
    question_text: str
    solution_steps: List[str]
    final_answer: str
    socratic_hints: List[Dict]
    difficulty: float
    marks: int
    source: str  # "pattern" or "ai"
    jsxgraph_code: Optional[str] = None
    generation_time_ms: float

class ExamRequest(BaseModel):
    chapters: List[int]
    total_marks: int = 80
    duration_minutes: int = 180
    student_id: Optional[str] = None

class ExamResponse(BaseModel):
    exam_id: str
    questions: List[Dict]
    total_marks: int
    duration_minutes: int
    stats: Dict

class AttemptRequest(BaseModel):
    question_id: str
    student_id: str
    answer: str
    time_taken_seconds: int

class AttemptResponse(BaseModel):
    is_correct: bool
    feedback: str
    next_difficulty: float
    recommendation: str

# Dependency injection
def get_orchestrator():
    """Get hybrid orchestrator singleton"""
    return get_hybrid_orchestrator(ai_ratio=0.5)  # 50-50 split


@router.post("/question/generate", response_model=QuestionResponse)
async def generate_question(
    request: QuestionRequest,
    orchestrator=Depends(get_orchestrator)
):
    """
    Generate a single question (50% Pattern / 50% AI)
    
    Examples:
    - concept: "trigonometry_heights"
    - concept: "quadratic_equations"
    - concept: "arithmetic_progression"
    """
    try:
        result = orchestrator.generate_question(
            concept=request.concept,
            marks=request.marks,
            difficulty=request.difficulty,
            force_source=request.force_source,
            student_id=request.student_id
        )
        
        return QuestionResponse(
            question_id=result.question_id,
            question_text=result.question_text,
            solution_steps=result.solution_steps,
            final_answer=result.final_answer,
            socratic_hints=result.socratic_hints,
            difficulty=result.difficulty,
            marks=result.marks,
            source=result.source,
            jsxgraph_code=result.jsxgraph_code,
            generation_time_ms=result.generation_time_ms
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/exam/generate", response_model=ExamResponse)
async def generate_exam(
    request: ExamRequest,
    orchestrator=Depends(get_orchestrator)
):
    """
    Generate complete CBSE exam with 50-50 Pattern/AI split
    """
    try:
        exam = orchestrator.generate_exam(
            chapters=request.chapters,
            total_marks=request.total_marks,
            duration_minutes=request.duration_minutes
        )
        
        return ExamResponse(
            exam_id=exam["exam_id"],
            questions=exam["questions"],
            total_marks=exam["total_marks"],
            duration_minutes=exam["duration_minutes"],
            stats={
                "ai_percentage": exam["ai_percentage"],
                "pattern_percentage": exam["pattern_percentage"],
                "total_questions": len(exam["questions"])
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exam generation failed: {str(e)}")


@router.post("/attempt/submit", response_model=AttemptResponse)
async def submit_attempt(
    request: AttemptRequest,
    orchestrator=Depends(get_orchestrator)
):
    """
    Submit student answer and get feedback
    """
    try:
        # This would integrate with VEDA for analysis
        # For now, mock implementation
        
        # Mock logic: compare answer (in real app, fetch question from DB)
        is_correct = random.random() > 0.3  # 70% correct rate for demo
        
        if is_correct:
            feedback = "✅ Correct! Well done. Ready for a harder question?"
            next_difficulty = min(1.0, 0.6 + 0.1)
            recommendation = "ai"  # Try creative AI question next
        else:
            feedback = "❌ Not quite. Let's review the steps and try a similar question."
            next_difficulty = max(0.2, 0.6 - 0.1)
            recommendation = "pattern"  # Stick to standard format
        
        return AttemptResponse(
            is_correct=is_correct,
            feedback=feedback,
            next_difficulty=next_difficulty,
            recommendation=recommendation
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Submission failed: {str(e)}")


@router.get("/stats")
async def get_stats(orchestrator=Depends(get_orchestrator)):
    """
    Get generation statistics and API costs
    """
    return orchestrator.get_stats()


@router.get("/concepts")
async def list_concepts():
    """
    List available concepts/topics for question generation
    """
    return {
        "concepts": [
            {
                "id": "trigonometry_heights",
                "name": "Heights and Distances",
                "chapters": [8],
                "marks_range": [2, 3, 5],
                "has_visual": True
            },
            {
                "id": "quadratic_equations",
                "name": "Quadratic Equations",
                "chapters": [4],
                "marks_range": [2, 3, 5],
                "has_visual": False
            },
            {
                "id": "arithmetic_progression",
                "name": "Arithmetic Progressions",
                "chapters": [5],
                "marks_range": [2, 3, 5],
                "has_visual": False
            },
            {
                "id": "circles_tangent",
                "name": "Circles - Tangent Properties",
                "chapters": [10],
                "marks_range": [2, 3, 5],
                "has_visual": True
            },
            {
                "id": "coordinate_distance",
                "name": "Coordinate Geometry - Distance",
                "chapters": [7],
                "marks_range": [2, 3],
                "has_visual": True
            },
            {
                "id": "triangles_similarity",
                "name": "Triangles - Similarity",
                "chapters": [6],
                "marks_range": [3, 5],
                "has_visual": True
            },
            {
                "id": "probability_basic",
                "name": "Probability - Basic",
                "chapters": [15],
                "marks_range": [1, 2],
                "has_visual": False
            },
            {
                "id": "mensuration_sector",
                "name": "Mensuration - Sector Areas",
                "chapters": [12],
                "marks_range": [3, 5],
                "has_visual": True
            }
        ]
    }


# Health check
@router.get("/health")
async def health_check():
    """API health status"""
    return {
        "status": "healthy",
        "service": "LOKAAH Hybrid ORACLE",
        "version": "2.0.0",
        "features": ["pattern_generation", "ai_generation", "jsxgraph_visuals"]
    }


# WebSocket for real-time question streaming (optional)
@router.websocket("/ws/practice")
async def practice_websocket(websocket: WebSocket):
    """
    WebSocket for real-time adaptive practice
    VEDA + ORACLE working together
    """
    await websocket.accept()
    await websocket.send_json({"message": "Connected to LOKAAH Practice Engine"})
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data["action"] == "get_question":
                concept = data.get("concept", "trigonometry_heights")
                difficulty = data.get("difficulty", 0.5)
                
                orch = get_hybrid_orchestrator()
                q = orch.generate_question(concept, 3, difficulty)
                
                await websocket.send_json({
                    "type": "question",
                    "data": {
                        "id": q.question_id,
                        "text": q.question_text,
                        "visual": q.jsxgraph_code,
                        "difficulty": q.difficulty,
                        "source": q.source
                    }
                })
                
            elif data["action"] == "submit_answer":
                # Process answer and send feedback
                is_correct = data["answer"] == data.get("expected_answer")
                await websocket.send_json({
                    "type": "feedback",
                    "correct": is_correct,
                    "next_concept": data["concept"] if is_correct else "review"
                })
                
    except Exception as e:
        await websocket.close()
