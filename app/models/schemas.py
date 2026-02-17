from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

# Request Models
class QuestionRequest(BaseModel):
    chapter: str = Field(..., min_length=1, max_length=200)
    concept: Optional[str] = Field(None, max_length=200)
    difficulty: float = Field(0.5, ge=0.0, le=1.0)
    user_id: Optional[str] = Field(None, max_length=100)
    session_id: Optional[str] = Field(None, max_length=100)

class AttemptRequest(BaseModel):
    question_id: str = Field(..., max_length=100)
    session_id: Optional[str] = Field(None, max_length=100)
    answer: Dict[str, Any]
    time_taken_seconds: Optional[int] = Field(None, ge=0, le=7200)
    hints_used: int = Field(0, ge=0, le=20)

class SessionCreateRequest(BaseModel):
    chapter: str = Field(..., min_length=1, max_length=200)
    concept: Optional[str] = Field(None, max_length=200)
    user_id: str = Field(..., min_length=1, max_length=100)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    session_id: Optional[str] = Field(None, max_length=100)
    user_profile: Dict[str, Any] = Field(default_factory=dict)
    force_agent: Optional[str] = Field(None, pattern=r"^(veda|oracle|spark|pulse|atlas)$")

# Response Models
class QuestionResponse(BaseModel):
    id: str
    text: str
    concept: str
    chapter: str
    difficulty: float
    source: str  # 'pattern' or 'ai'
    jsxgraph_code: Optional[str] = None
    hints: List[str] = []
    solution_steps: List[str] = []
    metadata: Dict[str, Any] = {}

class AttemptResponse(BaseModel):
    id: str
    is_correct: bool
    correct_answer: Dict[str, Any]
    feedback: str
    socratic_hint: Optional[str] = None
    progress_update: Dict[str, Any] = {}

class SessionResponse(BaseModel):
    id: str
    user_id: str
    chapter: str
    concept: Optional[str]
    current_difficulty: float
    status: str
    started_at: datetime

class VEDAInteraction(BaseModel):
    type: str  # 'hint', 'explanation', 'socratic_question'
    message: str
    context: Optional[Dict[str, Any]] = None

class HealthCheck(BaseModel):
    status: str
    database: str
    oracle_engine: str
    version: str = "1.0.0"


class ChatResponse(BaseModel):
    session_id: str
    response: str
    agent_name: str
    agent_label: str
    agent_emoji: str
    agent_color: str
