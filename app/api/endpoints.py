from fastapi import APIRouter, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator
from typing import AsyncGenerator, Optional, Dict, List
from pathlib import Path
import json
import asyncio
import logging
import uuid
import time
from collections import defaultdict

from app.core.config import settings
from app.core.database import (
    get_db, create_learning_session, save_question,
    record_attempt, get_user_profile, log_veda_interaction
)
from app.models.schemas import (
    QuestionRequest, AttemptRequest, SessionCreateRequest,
    QuestionResponse, AttemptResponse, SessionResponse, HealthCheck,
    ChatRequest, ChatResponse
)
from app.oracle.hybrid_orchestrator import get_hybrid_orchestrator
from app.agents.veda import VEDAAdapter
from app.graph.workflow import get_chat_runtime
from app.services.manim_generator import get_manim_generator
from app.services.photo_solver import get_photo_solver

router = APIRouter(prefix="/api/v1")

# ---------- Rate Limiter ----------
class RateLimiter:
    """Simple in-memory rate limiter per IP/session. Prevents API cost abuse."""
    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self._hits: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        hits = self._hits[key]
        # Prune expired entries
        self._hits[key] = [t for t in hits if now - t < self.window]
        if len(self._hits[key]) >= self.max_requests:
            return False
        self._hits[key].append(now)
        return True

_rate_limiter = RateLimiter(max_requests=30, window_seconds=60)

# Lazy initialization to avoid blocking imports
_orchestrator = None
_veda = None
_chat_runtime = None

def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = get_hybrid_orchestrator(ai_ratio=settings.AI_RATIO)
    return _orchestrator

def get_veda():
    global _veda
    if _veda is None:
        _veda = VEDAAdapter()
    return _veda

def get_chat_runtime_instance():
    global _chat_runtime
    if _chat_runtime is None:
        _chat_runtime = get_chat_runtime()
    return _chat_runtime

# ==========================================
# HEALTH & STATUS
# ==========================================

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Check system health"""
    db_status = "connected"
    try:
        db = get_db()
        db.table('profiles').select('count', count='exact').limit(1).execute()
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return HealthCheck(
        status="healthy",
        database=db_status,
        oracle_engine="ready"
    )

@router.get("/stats")
async def get_stats():
    """Get generation statistics"""
    return get_orchestrator().get_stats()


# ==========================================
# PROGRESS TRACKING & ANALYTICS
# ==========================================

class ProgressResponse(BaseModel):
    session_id: str
    total_questions_attempted: int
    total_correct: int
    accuracy: float
    concepts_practiced: List[Dict[str, Any]]
    weak_areas: List[str]
    mastered_topics: List[str]
    overall_mastery: float
    recommendations: List[str]

@router.get("/progress/{session_id}", response_model=ProgressResponse)
async def get_progress(session_id: str):
    """
    Get comprehensive progress report for a student session.
    Shows mastery scores, weak areas, and personalized recommendations.
    """
    try:
        db = get_db()
        
        # Get all concept mastery data for this session
        mastery_result = db.table('concept_mastery')\
            .select('*')\
            .eq('session_id', session_id)\
            .execute()
        
        concepts = mastery_result.data if mastery_result.data else []
        
        # Calculate aggregate statistics
        total_attempts = sum(c.get('attempts', 0) for c in concepts)
        total_correct = sum(c.get('correct_attempts', 0) for c in concepts)
        accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0.0
        
        # Identify weak areas (< 60% mastery) and mastered topics (> 85% mastery)
        weak_areas = [c['concept'] for c in concepts if c.get('score', 0.5) < 0.6]
        mastered_topics = [c['concept'] for c in concepts if c.get('score', 0.5) > 0.85]
        
        # Calculate overall mastery (weighted by attempts)
        if concepts:
            total_weight = sum(c.get('attempts', 0) for c in concepts)
            weighted_mastery = sum(
                c.get('score', 0.5) * c.get('attempts', 0) 
                for c in concepts
            )
            overall_mastery = weighted_mastery / total_weight if total_weight > 0 else 0.5
        else:
            overall_mastery = 0.0
        
        # Generate recommendations
        recommendations = []
        if weak_areas:
            recommendations.append(f"Focus on: {', '.join(weak_areas[:3])} - Practice 10 more questions each")
        if mastered_topics:
            recommendations.append(f"Great job on {', '.join(mastered_topics[:3])}! Keep that momentum going")
        if accuracy < 70:
            recommendations.append("Slow down and focus on understanding - accuracy is more important than speed")
        elif accuracy > 85:
            recommendations.append("Excellent accuracy! Ready for harder challenges?")
        if total_attempts < 10:
            recommendations.append("Keep practicing! Aim for at least 50 questions to see real progress")
        
        return ProgressResponse(
            session_id=session_id,
            total_questions_attempted=total_attempts,
            total_correct=total_correct,
            accuracy=round(accuracy, 1),
            concepts_practiced=concepts,
            weak_areas=weak_areas,
            mastered_topics=mastered_topics,
            overall_mastery=round(overall_mastery, 2),
            recommendations=recommendations
        )
        
    except Exception as e:
        logging.getLogger(__name__).exception("Progress tracking failed: %s", e)
        raise HTTPException(status_code=500, detail="Could not retrieve progress data")


# ==========================================
# SINGLE CHAT INTERFACE (LangGraph Supervisor)
# ==========================================

@router.post("/chat", response_model=ChatResponse)
async def single_chat(request: ChatRequest, req: Request):
    """
    One contact, multi-agent backend.
    Nirmola (supervisor) routes invisibly to VEDA / ORACLE / SPARK / PULSE / ATLAS.
    """
    # Rate limit by session or IP
    rate_key = request.session_id or req.client.host if req.client else "unknown"
    if not _rate_limiter.is_allowed(rate_key):
        raise HTTPException(status_code=429, detail="Too many requests. Please wait a moment.")

    try:
        result = await get_chat_runtime_instance().run_turn(
            message=request.message,
            session_id=request.session_id,
            user_profile=request.user_profile,
            force_agent=request.force_agent,
        )
        return ChatResponse(**result)
    except Exception as e:
        logging.getLogger(__name__).exception("Single chat failed: %s", e)
        raise HTTPException(status_code=500, detail="Hmm, I'm having trouble understanding that. Could you try rephrasing?")


@router.post("/chat/stream")
async def single_chat_stream(request: ChatRequest, req: Request):
    # Rate limit stream endpoint
    rate_key = request.session_id or (req.client.host if req.client else "unknown")
    if not _rate_limiter.is_allowed(rate_key):
        raise HTTPException(status_code=429, detail="Too many requests. Please wait a moment.")
    """
    SSE streaming version of /chat.
    Sends response token-by-token so the frontend shows progressive text.
    Event types: meta (agent info), token (text chunk), done (end signal), error.
    """

    async def _generate() -> AsyncGenerator[str, None]:
        try:
            result = await get_chat_runtime_instance().run_turn(
                message=request.message,
                session_id=request.session_id,
                user_profile=request.user_profile,
                force_agent=request.force_agent,
            )

            # Send agent metadata first so frontend can update theme immediately
            meta = {
                "session_id": result["session_id"],
                "agent_name": result["agent_name"],
                "agent_label": result["agent_label"],
                "agent_emoji": result["agent_emoji"],
                "agent_color": result["agent_color"],
            }
            yield f"event: meta\ndata: {json.dumps(meta)}\n\n"

            # Stream the response text in small chunks to simulate typing
            full_text = result.get("response", "")
            chunk_size = 4  # characters per chunk
            for i in range(0, len(full_text), chunk_size):
                chunk = full_text[i : i + chunk_size]
                yield f"event: token\ndata: {json.dumps({'text': chunk})}\n\n"
                await asyncio.sleep(0.02)  # 20ms per chunk for natural feel

            yield f"event: done\ndata: {json.dumps({'session_id': result['session_id']})}\n\n"

        except Exception as exc:
            logging.getLogger(__name__).exception("Stream failed: %s", exc)
            error_msg = "Hmm, I'm having trouble right now. Could you try again?"
            yield f"event: error\ndata: {json.dumps({'text': error_msg})}\n\n"

    return StreamingResponse(
        _generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

# ==========================================
# VEDA CHAT (Web App Integration)
# ==========================================

class VedaChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    session_id: Optional[str] = Field(None, max_length=100)

class VedaChatResponse(BaseModel):
    response: str
    session_id: str
    has_visual: bool = False
    visual_svg: Optional[str] = None
    formula_html: Optional[str] = None
    formula_latex: Optional[str] = None

# In-memory conversation history per session (bounded to prevent memory leaks)
_MAX_SESSIONS = 500
_chat_histories: Dict[str, List[Dict[str, str]]] = {}

@router.post("/veda/chat", response_model=VedaChatResponse)
async def veda_chat(request: VedaChatRequest):
    """
    Chat with VEDA AI tutor.
    Used by the web app frontend for real-time conversation.
    """
    try:
        session_id = request.session_id or f"web_{uuid.uuid4().hex[:12]}"

        # Get or create conversation history for this session (bounded)
        if session_id not in _chat_histories:
            if len(_chat_histories) >= _MAX_SESSIONS:
                # Evict oldest session
                oldest_key = next(iter(_chat_histories))
                del _chat_histories[oldest_key]
            _chat_histories[session_id] = []

        history = _chat_histories[session_id]

        # Call VEDA teach method
        result = await get_veda().agent.teach(
            student_message=request.message,
            session_id=session_id,
            conversation_history=history,
        )

        # Build response text from VEDA's structured output
        response_text = result.get("text", "")
        if result.get("socratic_question"):
            response_text += f"\n\n{result['socratic_question']}"
        if result.get("encouragement"):
            response_text += f"\n\n{result['encouragement']}"

        # If VEDA had an error/fallback, still return something useful
        if not response_text.strip():
            response_text = "I'm having a moment — could you rephrase your question?"

        # Extract visual data
        has_visual = result.get("has_visual", False)
        visual_svg = None
        if has_visual and result.get("visual_data"):
            visual_data = result["visual_data"]
            if hasattr(visual_data, "svg"):
                visual_svg = visual_data.svg
            elif isinstance(visual_data, dict):
                visual_svg = visual_data.get("svg")

        formula_html = result.get("formula_html")
        formula_latex = result.get("formula_latex")

        # Update conversation history
        history.append({"role": "user", "content": request.message})
        history.append({"role": "assistant", "content": response_text})

        # Keep history bounded
        if len(history) > 20:
            history[:] = history[-20:]

        return VedaChatResponse(
            response=response_text,
            session_id=session_id,
            has_visual=has_visual,
            visual_svg=visual_svg,
            formula_html=formula_html,
            formula_latex=formula_latex,
        )

    except Exception as e:
        logging.getLogger(__name__).exception("VEDA chat failed: %s", e)
        raise HTTPException(status_code=500, detail="I'm having a moment - could you rephrase your question?")


# ==========================================
# QUESTIONS
# ==========================================

@router.post("/question/generate", response_model=QuestionResponse)
async def generate_question(request: QuestionRequest):
    """
    Generate a single question with auto-difficulty
    - Uses Hybrid Oracle (50-50 Pattern/AI)
    - Saves to database if user_id provided
    - Returns JSXGraph code for visualization
    """
    try:
        # Generate question using hybrid orchestrator
        marks = int(request.difficulty * 4) + 1  # 1-5 marks
        result = get_orchestrator().generate_question(
            concept=f"{request.chapter}_{request.concept}" if request.concept else request.chapter,
            marks=marks,
            difficulty=request.difficulty,
        )
        
        # Convert socratic_hints (List[Dict]) to simple hints (List[str])
        hints = [hint.get('text', str(hint)) if isinstance(hint, dict) else str(hint) 
                 for hint in (result.socratic_hints or [])]
        
        # Format response
        question_data = {
            'id': result.question_id,
            'text': result.question_text,
            'concept': request.concept or request.chapter,
            'chapter': request.chapter,
            'difficulty': result.difficulty,
            'source': result.source,
            'jsxgraph_code': result.jsxgraph_code,
            'hints': hints,
            'solution_steps': result.solution_steps,
            'correct_answer': {'value': result.final_answer},
            'metadata': {
                'correct_answer': {'value': result.final_answer},
                'marks': result.marks,
                'variables': result.variables,
                'generation_time_ms': result.generation_time_ms
            }
        }
        
        # Save to database if session exists
        if request.session_id and request.user_id:
            try:
                saved = await save_question(request.session_id, request.user_id, question_data)
                if saved:
                    question_data['id'] = saved['id']
            except Exception as e:
                logging.getLogger(__name__).warning("Could not save to database: %s", e)
        
        return QuestionResponse(**question_data)
        
    except Exception as e:
        logging.getLogger(__name__).exception("Generation failed: %s", e)
        raise HTTPException(status_code=500, detail="Could not generate a question right now. Please try again.")

@router.post("/exam/generate")
async def generate_exam(chapter: str, user_id: str, question_count: int = 10):
    if question_count < 1 or question_count > 50:
        raise HTTPException(status_code=400, detail="question_count must be between 1 and 50")
    """
    Generate full CBSE-style exam (mixed difficulty)
    Alternates between Pattern and AI sources
    """
    questions = []
    difficulties = [0.3, 0.5, 0.7, 0.9] * (question_count // 4 + 1)
    
    for i in range(question_count):
        try:
            marks = int(difficulties[i] * 4) + 1
            result = get_orchestrator().generate_question(
                concept=chapter,
                marks=marks,
                difficulty=difficulties[i],
            )
            questions.append({
                'text': result.question_text,
                'difficulty': difficulties[i],
                'source': result.source,
                'jsxgraph_code': result.jsxgraph_code,
                'marks': result.marks,
                'solution_steps': result.solution_steps,
                'final_answer': result.final_answer
            })
        except Exception as e:
            continue
    
    return {
        "exam_id": f"exam_{chapter}_{user_id}",
        "chapter": chapter,
        "total_questions": len(questions),
        "questions": questions
    }

# ==========================================
# ATTEMPTS & ANSWERS
# ==========================================

@router.post("/attempt/submit", response_model=AttemptResponse)
async def submit_attempt(request: AttemptRequest, user_id: str):
    """
    Submit answer and get immediate feedback
    - Verifies answer correctness
    - Updates session difficulty
    - Returns VEDA feedback
    """
    try:
        # Fetch question correct answer from DB
        db = get_db()
        question = db.table('generated_questions').select('*').eq('id', request.question_id).single().execute()
        
        if not question.data:
            raise HTTPException(status_code=404, detail="Question not found")
        
        correct_answer = question.data['correct_answer']
        
        # Verify answer (simple comparison - enhance as needed)
        is_correct = False
        confidence = 0.0
        
        if 'value' in correct_answer:
            # Numeric answer
            student_val = request.answer.get('value')
            correct_val = correct_answer['value']
            tolerance = correct_answer.get('tolerance', 0.01)
            try:
                is_correct = abs(float(student_val) - float(correct_val)) <= tolerance
            except (TypeError, ValueError):
                is_correct = str(student_val).strip().lower() == str(correct_val).strip().lower()
            confidence = 1.0 if is_correct else 0.0
        elif 'coordinates' in correct_answer:
            # Graph-based answer (coordinates)
            student_coords = request.answer.get('coordinates', [])
            correct_coords = correct_answer['coordinates']
            # Calculate distance
            if len(student_coords) == len(correct_coords) == 2:
                dist = ((student_coords[0] - correct_coords[0])**2 + 
                       (student_coords[1] - correct_coords[1])**2)**0.5
                tolerance = correct_answer.get('tolerance', 0.5)
                is_correct = dist <= tolerance
                confidence = max(0, 1 - dist/tolerance) if not is_correct else 1.0
        
        # Record attempt
        attempt_data = {
            'answer': request.answer,
            'is_correct': is_correct,
            'confidence': confidence,
            'time_taken': request.time_taken_seconds,
            'hints_used': request.hints_used
        }
        
        if request.session_id:
            await record_attempt(request.question_id, user_id, request.session_id, attempt_data)
        
        # Get VEDA feedback
        feedback = await veda.generate_feedback(
            is_correct=is_correct,
            question_difficulty=question.data['difficulty'],
            attempts_count=request.hints_used + 1,
            concept=question.data['concept']
        )
        
        return AttemptResponse(
            id="attempt_temp",  # Replace with actual ID from DB
            is_correct=is_correct,
            correct_answer=correct_answer,
            feedback=feedback['message'],
            socratic_hint=feedback.get('hint'),
            progress_update={'mastery_change': 0.1 if is_correct else -0.05}
        )
        
    except Exception as e:
        logging.getLogger(__name__).exception("Submission failed: %s", e)
        raise HTTPException(status_code=500, detail="Could not process your answer. Please try again.")

# ==========================================
# SESSIONS
# ==========================================

@router.post("/session/start", response_model=SessionResponse)
async def start_session(request: SessionCreateRequest):
    """Start new learning session with VEDA"""
    try:
        # Validate user
        profile = await get_user_profile(request.user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create session
        session = await create_learning_session(
            user_id=request.user_id,
            chapter=request.chapter,
            concept=request.concept
        )
        
        # Initialize VEDA for this session
        await veda.initialize_session(
            user_id=request.user_id,
            chapter=request.chapter,
            concept=request.concept,
            proficiency=0.5
        )
        
        return SessionResponse(
            id=session['id'],
            user_id=session['user_id'],
            chapter=session['chapter'],
            concept=session['concept'],
            current_difficulty=session.get('current_difficulty', 0.5),
            status=session['status'],
            started_at=session['started_at']
        )
        
    except Exception as e:
        logging.getLogger(__name__).exception("Session creation failed: %s", e)
        raise HTTPException(status_code=500, detail="Could not start a new session. Please try again.")

@router.get("/session/{session_id}/status")
async def get_session_status(session_id: str, user_id: str):
    """Get current session progress"""
    try:
        db = get_db()
        session = db.table('learning_sessions').select('*').eq('id', session_id).single().execute()
        
        if not session.data or session.data['user_id'] != user_id:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get recent attempts
        attempts = db.table('student_attempts').select('*').eq('session_id', session_id).order('created_at', desc=True).limit(5).execute()
        
        return {
            "session": session.data,
            "recent_attempts": attempts.data if attempts.data else [],
            "veda_recommendation": await veda.get_recommendation(session_id)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# MANIM ANIMATIONS (Visual Explanations)
# ==========================================

@router.post("/animation/generate")
async def generate_animation(
    concept: str = Query(..., description="Concept name (e.g., 'quadratic_formula', 'pythagoras_theorem')"),
    quality: str = Query("medium_quality", pattern="^(low_quality|medium_quality|high_quality)$")
):
    """
    Generate Manim animation for a mathematical concept

    Available concepts:
    - quadratic_formula
    - pythagoras_theorem
    - linear_equation
    - area_of_circle

    Returns video path for download/streaming
    """
    try:
        manim_gen = get_manim_generator(quality=quality)

        # Check if concept exists
        if concept not in manim_gen.list_available_concepts():
            return {
                "success": False,
                "error": f"Concept '{concept}' not found",
                "available_concepts": manim_gen.list_available_concepts()
            }

        # Generate animation (async, may take 10-60 seconds depending on quality)
        result = await manim_gen.generate_animation(concept=concept)

        if result.success:
            return {
                "success": True,
                "concept": concept,
                "video_path": result.video_path,
                "message": "Animation generated successfully. Use /animation/serve to download."
            }
        else:
            return {
                "success": False,
                "error": result.error
            }

    except Exception as exc:
        logging.getLogger(__name__).exception("Animation generation failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Animation generation failed: {str(exc)}")

@router.get("/animation/list")
async def list_animations():
    """List all available pre-defined concept animations"""
    manim_gen = get_manim_generator()
    return {
        "concepts": manim_gen.list_available_concepts(),
        "count": len(manim_gen.list_available_concepts())
    }

@router.get("/animation/serve/{concept}")
async def serve_animation(concept: str):
    """
    Serve generated animation video file

    Note: In production, videos should be served via CDN (S3, Cloudflare R2, etc.)
    This endpoint is for development/testing only.
    """
    try:
        from fastapi.responses import FileResponse
        import os

        manim_gen = get_manim_generator()

        # Check cache
        cache_key = f"template_{concept}"
        video_path = manim_gen.output_dir / f"{cache_key}.mp4"

        if not video_path.exists():
            # Generate if not cached
            result = await manim_gen.generate_animation(concept=concept)
            if not result.success:
                raise HTTPException(status_code=404, detail=f"Failed to generate animation: {result.error}")
            video_path = Path(result.video_path)

        if not video_path.exists():
            raise HTTPException(status_code=404, detail=f"Video not found for concept '{concept}'")

        return FileResponse(
            path=str(video_path),
            media_type="video/mp4",
            filename=f"{concept}.mp4"
        )

    except Exception as exc:
        logging.getLogger(__name__).exception("Animation serving failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))

# ==========================================
# PHOTO SOLVER (Multi-Subject Question Solver)
# ==========================================

@router.post("/photo/solve")
async def solve_photo_question(
    request: Request,
    subject: str = Query("mathematics", pattern="^(mathematics|physics|chemistry|biology|social_science|english)$"),
    session_id: Optional[str] = Query(None, max_length=100),
    language: str = Query("english", max_length=50),
    store_in_db: bool = Query(True)
):
    """
    Solve question from uploaded image using Gemini Vision

    Supports ALL CBSE Class 10 subjects:
    - mathematics
    - physics
    - chemistry
    - biology
    - social_science (History, Geography, Civics, Economics)
    - english (Grammar, Literature, Writing)

    Request:
        - Content-Type: multipart/form-data
        - Field 'image': Image file (JPG, PNG, HEIC, WebP)
        - Query params: subject, session_id, language, store_in_db

    Response:
        - question_text: Extracted question
        - solution: Step-by-step solution
        - explanation: Conceptual understanding
        - key_concepts: List of concepts used
        - difficulty_level: 0.0 to 1.0
        - confidence: AI confidence (0.0 to 1.0)
    """
    try:
        # Get image from form data
        form = await request.form()
        image_file = form.get("image")

        if not image_file:
            raise HTTPException(status_code=400, detail="No image file provided")

        # Read image bytes
        image_data = await image_file.read()

        if len(image_data) == 0:
            raise HTTPException(status_code=400, detail="Empty image file")

        # Validate file size (max 10MB)
        if len(image_data) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

        # Solve using Gemini Vision
        solver = get_photo_solver()
        result = await solver.solve_from_image(
            image_data=image_data,
            subject=subject,
            session_id=session_id or f"photo_{uuid.uuid4().hex[:8]}",
            language=language,
            store_in_db=store_in_db
        )

        if result.success:
            return {
                "success": True,
                "question_text": result.question_text,
                "subject": result.subject,
                "chapter": result.chapter,
                "solution": result.solution,
                "explanation": result.explanation,
                "key_concepts": result.key_concepts,
                "difficulty_level": result.difficulty_level,
                "language": result.language,
                "confidence": result.confidence
            }
        else:
            raise HTTPException(status_code=500, detail=result.error)

    except HTTPException:
        raise
    except Exception as exc:
        logging.getLogger(__name__).exception("Photo solving failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Photo solving failed: {str(exc)}")

@router.get("/photo/subjects")
async def list_photo_subjects():
    """List all supported subjects for photo solving"""
    solver = get_photo_solver()
    return {
        "subjects": solver.list_supported_subjects(),
        "count": len(solver.list_supported_subjects())
    }

@router.get("/photo/history/{session_id}")
async def get_photo_history(session_id: str):
    """Get all previously solved photos for a session"""
    try:
        db = get_db()
        results = db.table('solved_questions')\
            .select('*')\
            .eq('session_id', session_id)\
            .order('solved_at', desc=True)\
            .limit(50)\
            .execute()

        if results.data:
            return {
                "session_id": session_id,
                "count": len(results.data),
                "questions": results.data
            }
        else:
            return {
                "session_id": session_id,
                "count": 0,
                "questions": []
            }

    except Exception as exc:
        logging.getLogger(__name__).exception("Failed to fetch photo history: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))

# ==========================================
# WEBSOCKET (Real-time Practice)
# ==========================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_personal_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/practice/{session_id}")
async def websocket_practice(websocket: WebSocket, session_id: str):
    """
    WebSocket for real-time adaptive practice
    - VEDA provides live hints
    - Difficulty adjusts based on performance
    - Real-time JSXGraph updates
    """
    await manager.connect(websocket, session_id)
    
    try:
        # Load session context
        db = get_db()
        session = db.table('learning_sessions').select('*').eq('id', session_id).single().execute()
        
        if not session.data:
            await websocket.send_json({"error": "Session not found"})
            return
        
        user_id = session.data['user_id']
        await veda.initialize_session(user_id, session.data['chapter'], session.data['concept'])
        
        await websocket.send_json({
            "type": "welcome",
            "message": "VEDA is ready to guide you",
            "session_id": session_id
        })
        
        while True:
            data = await websocket.receive_json()
            action = data.get('action')
            
            if action == 'request_question':
                # Generate and send question
                current_difficulty = session.data.get('current_difficulty', 0.5)
                result = get_orchestrator().generate_question(
                    concept=session.data['concept'] or session.data['chapter'],
                    marks=int(current_difficulty * 4) + 1,
                    difficulty=current_difficulty,
                )
                
                # Save question
                question_data = {
                    'text': result.question_text,
                    'concept': session.data.get('concept', session.data['chapter']),
                    'chapter': session.data['chapter'],
                    'difficulty': current_difficulty,
                    'source': result.source,
                    'jsxgraph_code': result.jsxgraph_code,
                    'hints': [str(h) for h in (result.socratic_hints or [])],
                    'solution_steps': result.solution_steps,
                    'correct_answer': {'value': result.final_answer},
                }
                saved = await save_question(session_id, user_id, question_data)
                
                await manager.send_personal_message({
                    "type": "question",
                    "question_id": saved['id'] if saved else result.question_id,
                    "text": result.question_text,
                    "jsxgraph_code": result.jsxgraph_code,
                    "difficulty": current_difficulty
                }, session_id)
            
            elif action == 'submit_answer':
                # Process answer and adapt
                is_correct = data.get('is_correct', False)
                
                # Update session difficulty (VEDA logic)
                new_difficulty = await veda.adapt_difficulty(
                    session_id=session_id,
                    current_difficulty=session.data.get('current_difficulty', 0.5),
                    is_correct=is_correct
                )
                
                # Update DB
                db.table('learning_sessions').update({
                    'current_difficulty': new_difficulty
                }).eq('id', session_id).execute()
                session.data['current_difficulty'] = new_difficulty
                
                # Generate feedback
                feedback = await veda.generate_feedback(
                    is_correct=is_correct,
                    question_difficulty=session.data.get('current_difficulty', 0.5),
                    attempts_count=data.get('attempt_count', 1),
                    concept=session.data.get('concept', session.data['chapter'])
                )
                
                await manager.send_personal_message({
                    "type": "feedback",
                    "is_correct": is_correct,
                    "message": feedback['message'],
                    "new_difficulty": new_difficulty,
                    "hint": feedback.get('hint')
                }, session_id)
            
            elif action == 'request_hint':
                hint = await veda.get_hint(
                    question_id=data.get('question_id'),
                    hint_level=data.get('level', 1)
                )
                await manager.send_personal_message({
                    "type": "hint",
                    "hint": hint,
                    "level": data.get('level', 1)
                }, session_id)
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        manager.disconnect(session_id)
