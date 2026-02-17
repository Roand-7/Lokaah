# 🛠️ Quick Fluidity Fixes (P0)
**Implementation Time: 2-3 hours**

These are the fastest high-impact fixes to make the UX feel less robotic.

---

## FIX #1: Strip Debug Metadata (30 minutes)

### Problem
API response exposes internal routing logic:
```json
{
  "response": "Great question!",
  "route_reason": "explanation/teaching/general math chat",
  "route_confidence": 0.923,
  "runtime_mode": "fallback",
  "payload": {
    "question_id": "PAT_trig_3421",
    "pattern_id": "trigonometry_heights",
    "variables": {"angle": 60}
  }
}
```

Users see "source: pattern" and "confidence: 0.92" → feels like debugging tool, not conversation.

### Solution

**File:** `app/api/endpoints.py`

**Step 1:** Add settings check (line 15)
```python
from app.core.config import settings

DEBUG_MODE = settings.DEBUG
```

**Step 2:** Sanitize response before returning (line 85)
```python
@router.post("/chat", response_model=ChatResponse)
async def single_chat(request: ChatRequest):
    try:
        result = await get_chat_runtime_instance().run_turn(
            user_message=request.message,
            session_id=request.session_id or "",
            user_profile=request.user_profile or {},
            force_agent=request.force_agent
        )
        
        # 🔧 STRIP DEBUG INFO IN PRODUCTION
        if not DEBUG_MODE:
            result["route_reason"] = None
            result["route_confidence"] = None
            result["runtime_mode"] = "production"
            
            # Sanitize payload - remove technical IDs
            if "payload" in result and result["payload"]:
                payload = result["payload"]
                payload.pop("question_id", None)
                payload.pop("pattern_id", None)
                payload.pop("variables", None)
                payload.pop("socratic_hints", None)
                # Keep only user-facing data
                result["payload"] = {
                    k: v for k, v in payload.items()
                    if k in ["marks", "topic", "difficulty", "jsxgraph_code"]
                }
        
        return ChatResponse(**result)
```

**Step 3:** Update `.env.example`
```bash
# Set to true for development (shows routing debug info)
# Set to false for production (clean API responses)
DEBUG=false
```

**Test:**
```powershell
# Production mode
$env:DEBUG="false"; python main.py
# Send chat message, verify no route_reason in response

# Debug mode (for development)
$env:DEBUG="true"; python main.py
# Send chat message, verify route_reason is present
```

---

## FIX #2: Humanize Oracle Responses (45 minutes)

### Problem
Oracle returns templated intros:
```
Challenge accepted. High-focus mode ON.

[3 marks | source: pattern]
A ladder leans against a wall...

Reply with your final answer, and I will evaluate it instantly.
```

Feels like a form, not a conversation.

### Solution

**File:** `app/graph/nodes/oracle.py`

**Replace:** `_render_question()` method (line 119)

```python
async def _render_question(self, question_text: str, marks: int, source: str, topic: str) -> str:
    """
    Generate natural conversational wrapper for question.
    Uses LLM micro-prompt instead of hardcoded template.
    """
    # Determine agent personality
    agent_name = "Spark" if self.mode == "spark" else "Oracle"
    tone = "challenging and energetic" if self.mode == "spark" else "encouraging and supportive"
    
    # Micro-prompt for humanization
    humanize_prompt = f"""
You are {agent_name}, an AI math practice assistant.

TASK: Present this question to the student in a natural, conversational way.

QUESTION: {question_text}
MARKS: {marks}
TOPIC: {topic}
MODE: {self.mode}

TONE: {tone}

GUIDELINES:
- Start with a warm intro (1 sentence, no robotic phrases like "Challenge accepted")
- Present the question naturally (don't say "[3 marks | source: pattern]")
- End with an encouraging prompt (NOT "Reply with your final answer")
- Keep it concise (max 4 sentences total)
- Sound like a real tutor, not a textbook

OUTPUT FORMAT (plain text only, no markdown):
"""
    
    try:
        # Use Gemini with low temperature for consistent style
        from app.core.config import settings
        from google import genai
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=humanize_prompt,
            config={'temperature': 0.4}  # Low for consistency
        )
        
        humanized = response.text.strip()
        
        # Fallback if LLM returns empty
        if not humanized:
            raise ValueError("Empty response from humanizer")
        
        return humanized
        
    except Exception as e:
        logger.warning(f"Humanizer failed: {e}, using fallback")
        # Improved fallback (still better than old template)
        intro = "Alright, here's a focused challenge for you." if self.mode == "spark" else "Let's try this one."
        return f"{intro}\n\n{question_text}\n\nTake your time and show your reasoning."
```

**Add import at top of file:**
```python
import logging
logger = logging.getLogger(__name__)
```

**Update call site** (line 95):
```python
# OLD
question_rendered = self._render_question(
    question_text=question_data.get("question_text", ""),
    marks=question_data.get("marks", 3),
    source=question_data.get("source", "unknown")
)

# NEW
question_rendered = await self._render_question(
    question_text=question_data.get("question_text", ""),
    marks=question_data.get("marks", 3),
    source=question_data.get("source", "unknown"),
    topic=question_data.get("topic", "Mathematics")
)
```

**Make node method async** (line 36):
```python
# OLD
def run(self, state: Dict[str, Any]) -> Dict[str, Any]:

# NEW
async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
```

**Test:**
```powershell
python -c "
from app.api import endpoints
import asyncio

async def test():
    request = endpoints.ChatRequest(
        message='/test trigonometry easy',
        session_id='test_123'
    )
    response = await endpoints.single_chat(request)
    print(response.response)
    # Should see natural intro like:
    # 'Alright, here's a good warm-up problem...'
    # NOT 'Here is your next practice question.'

asyncio.run(test())
"
```

---

## FIX #3: Humanize Atlas Responses (45 minutes)

### Problem
Atlas dumps JSON data as bullet list:
```
Exam window: March 2026
Next high-impact plan:
- Day 1: Algebra revision (60m)
- Day 2: Geometry practice (45m)
If you want, I can convert this into a daily checklist now.
```

No personality, just data formatting.

### Solution

**File:** `app/graph/nodes/atlas.py`

**Replace entire `_build_schedule_reply()` method** (line 43):

```python
async def _build_schedule_reply(self, user_text: str) -> str:
    """
    Generate natural conversational schedule summary using LLM.
    Passes schedule data to Atlas persona for warm, motivational response.
    """
    # Extract schedule data
    exam_window = self.schedule_data.get("exam_window", "Not set")
    plan = self.schedule_data.get("weekly_plan", [])[:3]  # Next 3 days
    
    if not plan:
        return (
            "Hmm, I don't see any schedule saved yet. "
            "Want to set up your study plan together? Just tell me when your exam is."
        )
    
    # Build context for LLM
    schedule_context = f"Exam: {exam_window}\n"
    for item in plan:
        schedule_context += f"- {item.get('day')}: {item.get('focus')} ({item.get('duration')})\n"
    
    # Atlas persona prompt
    atlas_prompt = f"""
You are Atlas, a strategic study planner. Your role is to help students plan their exam preparation.

USER ASKED: "{user_text}"

STUDENT'S SCHEDULE DATA:
{schedule_context}

TASK: Present this schedule in a warm, motivational way.

GUIDELINES:
- Start with encouragement (acknowledge their exam timeline)
- Summarize the plan naturally (NO bullet points with dashes)
- Suggest next steps or offer customization
- Sound like a coach, not a calendar app
- Keep it concise (3-4 sentences)
- Use phrases like "Here's what we've mapped out", "Your game plan", "Let's tackle"

OUTPUT (plain text only):
"""
    
    try:
        from app.core.config import settings
        from google import genai
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=atlas_prompt,
            config={'temperature': 0.6}  # Moderate for personality
        )
        
        humanized = response.text.strip()
        
        if not humanized:
            raise ValueError("Empty Atlas response")
        
        return humanized
        
    except Exception as e:
        logger.warning(f"Atlas humanizer failed: {e}")
        # Better fallback than old template
        return (
            f"Alright, here's your game plan leading up to {exam_window}. "
            f"We've got {len(plan)} focused sessions lined up, starting with {plan[0].get('focus')}. "
            "Want me to adjust anything or dive into specifics?"
        )
```

**Make node method async** (line 36):
```python
# OLD
def run(self, state: Dict[str, Any]) -> Dict[str, Any]:

# NEW
async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
```

**Update call site** (line 39):
```python
# OLD
reply_text = self._build_schedule_reply(user_text)

# NEW
reply_text = await self._build_schedule_reply(user_text)
```

**Add import:**
```python
import logging
logger = logging.getLogger(__name__)
```

**Test:**
```powershell
python -c "
from app.graph.nodes.atlas import AtlasNode
import asyncio

async def test():
    atlas = AtlasNode()
    state = {
        'messages': [{'role': 'user', 'content': 'Show me my plan'}],
        'session_id': 'test'
    }
    result = await atlas.run(state)
    print(result['response']['text'])
    # Should see natural response like:
    # 'Here's your game plan for March 2026...'
    # NOT 'Exam window: March 2026\\nNext high-impact plan:'

asyncio.run(test())
"
```

---

## FIX #4: Mask Error Messages (15 minutes)

### Problem
Raw exceptions exposed to user:
```json
{
  "detail": "Single chat failed: name 'veda' is not defined"
}
```

### Solution

**File:** `app/api/endpoints.py`

**Update exception handler** (line 92):

```python
@router.post("/chat", response_model=ChatResponse)
async def single_chat(request: ChatRequest):
    try:
        # ... existing code ...
        return ChatResponse(**result)
    
    except Exception as e:
        logger.exception("Chat API error: %s", e)
        
        # Debug mode: show raw error
        if DEBUG_MODE:
            raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
        
        # Production mode: graceful fallback
        return ChatResponse(
            session_id=request.session_id or "error_session",
            response=(
                "Hmm, I'm having a bit of trouble thinking right now. "
                "Can you try rephrasing that, or ask something else?"
            ),
            agent_name="veda",
            agent_label="VEDA",
            agent_emoji="⚠️",
            agent_color="blue",
            route_reason=None,
            route_confidence=None,
            runtime_mode="error_fallback",
            payload=None
        )
```

**Test:**
```powershell
# Cause intentional error (invalid session_id format)
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "session_id": null}'

# Production mode should return:
# "Hmm, I'm having a bit of trouble thinking right now..."
# NOT raw exception
```

---

## 🧪 VERIFICATION CHECKLIST

After implementing all 4 fixes:

- [ ] **Debug Stripping:** 
  - Set `DEBUG=false` in `.env`
  - Send chat message
  - Verify response has NO `route_reason`, `route_confidence`, or internal IDs

- [ ] **Oracle Humanization:**
  - Request `/test trigonometry`
  - Verify intro is natural ("Alright, here's one for you...")
  - Verify NO "[3 marks | source: pattern]" text

- [ ] **Atlas Humanization:**
  - Request `/plan` or "show my schedule"
  - Verify response is conversational ("Here's your game plan...")
  - Verify NO bullet list with dashes

- [ ] **Error Masking:**
  - Cause intentional error (invalid input)
  - Verify user sees friendly message
  - Verify NO stack trace or Python exception

---

## 📊 IMPACT ESTIMATE

| Metric | Before | After | Time Investment |
|--------|--------|-------|-----------------|
| **Debug Leakage** | 🚨 Exposed | ✅ Hidden | 30 min |
| **Oracle Fluidity** | 3/10 (templated) | 7/10 (natural) | 45 min |
| **Atlas Fluidity** | 2/10 (data dump) | 8/10 (conversational) | 45 min |
| **Error UX** | 1/10 (stack traces) | 9/10 (graceful) | 15 min |
| **Overall Fluidity** | 6.5/10 | **8.5/10** | **2h 15m** |

**ROI:** +2 fluidity points in ~2 hours of work.

---

## 🚀 DEPLOYMENT ORDER

1. **Fix #4 (Error Masking)** - Deploy first (safest, prevents user-facing bugs)
2. **Fix #1 (Debug Stripping)** - Deploy second (no behavior change, just cleanup)
3. **Fix #3 (Atlas Humanization)** - Deploy third (low traffic, test LLM integration)
4. **Fix #2 (Oracle Humanization)** - Deploy last (highest traffic, monitor closely)

---

## 📝 ROLLBACK PLAN

If humanization causes issues (slow LLM calls, nonsensical responses):

**Emergency Rollback:**
```python
# In oracle.py / atlas.py, change async method back:
async def _render_question(...):
    # return await humanize_with_llm(...)  # NEW (problematic)
    return f"{intro}\n\n{question_text}\n\n{outro}"  # OLD (rollback)
```

**Keep error masking & debug stripping** - those are pure improvements.

---

**Created:** February 16, 2026  
**Total Time:** 2-3 hours  
**Fluidity Gain:** +2 points (6.5 → 8.5)  
**Risk Level:** Low (incremental changes with fallbacks)
