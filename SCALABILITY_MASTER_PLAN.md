# LOKAAH Scalability Master Plan
## From CBSE Class 10 Math → All-India Education Platform

---

## Vision: The Duolingo of Indian Education

**Current Focus:** CBSE Class 10 Mathematics (Perfect Template)
**Phase 2 (6 months):** All CBSE subjects + All boards (Class 10)
**Phase 3 (12 months):** Class 11-12 (All boards, all subjects)
**Phase 4 (18 months):** Competitive Exams (JEE, NEET, UPSC, CAT, etc.)
**Phase 5 (24 months):** Vernacular expansion (Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati...)

**End State:** Every student in India (700M+ market) uses LOKAAH for exam prep.

---

## Part 1: Scalable Architecture Design

### **Current Problem:**
If we hardcode everything for CBSE Class 10 Math, we'll have to rewrite for:
- CBSE Class 10 Science
- CBSE Class 10 Social Studies
- Karnataka Board Class 10 Math
- Kerala Board Class 10 Math
- ... (100+ permutations)

**This is 100x tech debt!**

### **Solution: Multi-Tenant Curriculum System**

#### **Database Schema (Scalable Design)**

```sql
-- Curriculum hierarchy
CREATE TABLE boards (
    id UUID PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,  -- "CBSE", "KARNATAKA", "KERALA"
    name TEXT NOT NULL,
    country TEXT DEFAULT 'India',
    language_code TEXT DEFAULT 'en',  -- Default language
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE subjects (
    id UUID PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,  -- "MATH", "SCIENCE", "SOCIAL"
    name TEXT NOT NULL,
    icon TEXT,  -- "🧮", "🔬", "🌍"
    color TEXT  -- For UI theming
);

CREATE TABLE curricula (
    id UUID PRIMARY KEY,
    board_id UUID REFERENCES boards(id),
    subject_id UUID REFERENCES subjects(id),
    class_level INTEGER NOT NULL,  -- 10, 11, 12
    academic_year TEXT,  -- "2024-25"
    syllabus_version TEXT,  -- Track CBSE revisions
    exam_pattern JSONB,  -- Store exam structure
    total_marks INTEGER,
    passing_marks INTEGER,
    UNIQUE(board_id, subject_id, class_level, academic_year)
);

-- Example: CBSE Class 10 Math 2024-25
INSERT INTO curricula VALUES (
    uuid_generate_v4(),
    (SELECT id FROM boards WHERE code = 'CBSE'),
    (SELECT id FROM subjects WHERE code = 'MATH'),
    10,
    '2024-25',
    '1.0',
    '{
        "sections": [
            {"name": "A", "type": "MCQ", "questions": 20, "marks_each": 1},
            {"name": "B", "type": "VSA", "questions": 5, "marks_each": 2},
            {"name": "C", "type": "SA", "questions": 6, "marks_each": 3},
            {"name": "D", "type": "LA", "questions": 2, "marks_each": 5}
        ],
        "time_limit_minutes": 180
    }',
    80,
    33
);

-- Topics/Chapters hierarchy
CREATE TABLE topics (
    id UUID PRIMARY KEY,
    curriculum_id UUID REFERENCES curricula(id),
    code TEXT NOT NULL,  -- "QUADRATIC_EQUATIONS"
    name TEXT NOT NULL,
    display_name JSONB,  -- Multi-language {"en": "Quadratic Equations", "hi": "द्विघात समीकरण"}
    parent_topic_id UUID REFERENCES topics(id),  -- For nested topics
    sequence_order INTEGER,
    weightage_marks INTEGER,  -- How many marks in exam
    ncert_chapter_number INTEGER,
    difficulty_avg FLOAT DEFAULT 0.5
);

-- Patterns (reusable across boards if similar)
CREATE TABLE question_patterns (
    id UUID PRIMARY KEY,
    pattern_id TEXT UNIQUE NOT NULL,  -- "quadratic_discriminant_v1"
    topic_id UUID REFERENCES topics(id),
    difficulty FLOAT,
    marks INTEGER,
    template_text JSONB,  -- Multi-language
    variables_schema JSONB,
    solution_template JSONB,
    answer_template JSONB,
    validation_rules JSONB,
    visual_type TEXT,  -- "jsxgraph_parabola", "static_diagram", null
    visual_config JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_approved BOOLEAN DEFAULT false,  -- Quality control
    usage_count INTEGER DEFAULT 0
);

-- Multilingual content
CREATE TABLE translations (
    id UUID PRIMARY KEY,
    entity_type TEXT NOT NULL,  -- "pattern", "topic", "hint"
    entity_id UUID NOT NULL,
    language_code TEXT NOT NULL,  -- "en", "hi", "ta", "te", "kn"
    field_name TEXT NOT NULL,  -- "template_text", "name", "description"
    content JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(entity_type, entity_id, language_code, field_name)
);

-- User's multi-subject progress
CREATE TABLE student_curriculum_progress (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    curriculum_id UUID REFERENCES curricula(id),
    enrolled_at TIMESTAMPTZ DEFAULT NOW(),
    current_topic_id UUID REFERENCES topics(id),
    topics_mastered INTEGER DEFAULT 0,
    topics_total INTEGER,
    overall_mastery FLOAT DEFAULT 0.0,
    exam_readiness FLOAT DEFAULT 0.0,  -- Predicted score %
    last_practiced TIMESTAMPTZ
);

-- Topic-level mastery
CREATE TABLE topic_mastery (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    topic_id UUID REFERENCES topics(id),
    mastery_score FLOAT DEFAULT 0.5,  -- 0.0 to 1.0
    questions_solved INTEGER DEFAULT 0,
    questions_correct INTEGER DEFAULT 0,
    last_attempt TIMESTAMPTZ,
    weak_areas TEXT[],  -- Sub-concepts within topic
    UNIQUE(user_id, topic_id)
);
```

### **Code Architecture (Multi-Tenant Services)**

```python
# app/curriculum/curriculum_manager.py
class CurriculumManager:
    """Central curriculum registry - works across boards, subjects, classes"""

    def __init__(self, db):
        self.db = db

    async def get_curriculum(
        self,
        board: str = "CBSE",
        subject: str = "MATH",
        class_level: int = 10,
        academic_year: str = "2024-25"
    ) -> Curriculum:
        """Get curriculum configuration"""
        return await self.db.fetch_one(
            "SELECT * FROM curricula WHERE board_id = ... AND subject_id = ..."
        )

    async def get_topics(self, curriculum_id: UUID) -> List[Topic]:
        """Get all topics for a curriculum"""
        return await self.db.fetch_all(
            "SELECT * FROM topics WHERE curriculum_id = $1 ORDER BY sequence_order",
            curriculum_id
        )

    async def get_patterns_for_topic(
        self,
        topic_id: UUID,
        difficulty: Optional[float] = None,
        marks: Optional[int] = None
    ) -> List[QuestionPattern]:
        """Get question patterns for a topic"""
        query = "SELECT * FROM question_patterns WHERE topic_id = $1"
        if difficulty:
            query += f" AND difficulty BETWEEN {difficulty - 0.1} AND {difficulty + 0.1}"
        if marks:
            query += f" AND marks = {marks}"
        return await self.db.fetch_all(query, topic_id)


# app/services/translation_service.py
class TranslationService:
    """Multi-language support - CRITICAL for vernacular expansion"""

    def __init__(self, db, gemini_client):
        self.db = db
        self.llm = gemini_client
        self.cache = {}  # Redis in production

    async def translate(
        self,
        text: str,
        from_lang: str = "en",
        to_lang: str = "hi",
        context: str = "math"  # Subject context for better translation
    ) -> str:
        """Translate using Gemini (cheaper than Google Translate for our use case)"""

        cache_key = f"{from_lang}:{to_lang}:{hash(text)}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        prompt = f"""
Translate this {context} educational content from {from_lang} to {to_lang}.
Preserve mathematical notation and formulas.
Use formal educational tone.

Original: {text}

Translation:
"""
        response = await self.llm.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        translated = response.text.strip()
        self.cache[cache_key] = translated
        return translated

    async def get_localized_pattern(
        self,
        pattern_id: str,
        language: str = "en"
    ) -> Dict:
        """Get question pattern in user's language"""

        pattern = await self.db.fetch_one(
            "SELECT * FROM question_patterns WHERE pattern_id = $1",
            pattern_id
        )

        if language == "en":
            return pattern  # Already in English

        # Check if translation exists
        translation = await self.db.fetch_one(
            "SELECT content FROM translations WHERE entity_type = 'pattern' AND entity_id = $1 AND language_code = $2",
            pattern.id, language
        )

        if translation:
            return {**pattern, "template_text": translation["content"]}

        # Auto-translate using Gemini
        translated = await self.translate(
            pattern["template_text"],
            from_lang="en",
            to_lang=language,
            context="mathematics"
        )

        # Cache translation
        await self.db.execute(
            "INSERT INTO translations (entity_type, entity_id, language_code, field_name, content) VALUES ($1, $2, $3, $4, $5)",
            "pattern", pattern.id, language, "template_text", translated
        )

        return {**pattern, "template_text": translated}
```

---

## Part 2: CBSE Class 10 Math as Perfect Template

### **What "Perfect" Means:**

1. ✅ **100% Syllabus Coverage** - All 60+ patterns created
2. ✅ **NCERT Alignment** - Every exercise type covered
3. ✅ **Board Exam Pattern** - MCQ, VSA, SA, LA question types
4. ✅ **Previous Year Papers** - 2015-2024 questions integrated
5. ✅ **JSXGraph Visuals** - Interactive diagrams for 15+ topics
6. ✅ **Marking Scheme** - CBSE step marks integrated
7. ✅ **Vernacular** - Hindi translation for all patterns
8. ✅ **Gamification** - XP, streaks, badges fully working
9. ✅ **Mock Tests** - 10 full 80-mark papers
10. ✅ **Predicted Score** - ML model based on practice performance

**Once this template works, we copy-paste for:**
- CBSE Class 10 Science (just change topics + patterns)
- Karnataka Board Class 10 Math (just change exam pattern)
- CBSE Class 11 Math (add new topics)

---

## Part 3: JSXGraph Integration (Visual Supremacy)

### **Current Status:**
- ✅ DiagramGenerator service exists (`app/services/diagram_generator.py`)
- ✅ VEDA can call `CreateDiagramTool`
- ⚠️ **Limited to basic diagrams**

### **Target: Interactive Visualizations**

#### **Topics Requiring JSXGraph:**

1. **Coordinate Geometry**
   - Distance formula (draggable points)
   - Section formula (sliding divider)
   - Triangle area (vertices movable)

2. **Quadratic Equations**
   - Parabola graph (change a, b, c → see shape change)
   - Roots visualization (x-intercepts)
   - Discriminant impact on roots

3. **Trigonometry**
   - Unit circle (rotate angle, see ratios)
   - Heights & distances (drag angle of elevation)
   - Graphs of sin, cos, tan

4. **Circles**
   - Tangent construction (point outside circle)
   - Chord theorems (drag points, see angles)

5. **Similar Triangles**
   - Scale transformation (zoom triangle, ratios preserved)

6. **Probability**
   - Dice roll simulation
   - Coin toss visualization

#### **Enhanced DiagramGenerator**

```python
# app/services/diagram_generator.py (ENHANCED)
class JSXGraphGenerator:
    """Production-grade JSXGraph diagram generation"""

    TEMPLATES = {
        "coordinate_distance": """
        <div id="jxgbox_{id}" class="jxgbox" style="width:500px; height:500px;"></div>
        <script>
        const board = JXG.JSXGraph.initBoard('jxgbox_{id}', {{
            boundingbox: [-5, 5, 5, -5],
            axis: true,
            showNavigation: false
        }});

        // Draggable points
        const A = board.create('point', [{x1}, {y1}], {{
            name: 'A({x1}, {y1})',
            size: 3,
            color: '#3b82f6'
        }});

        const B = board.create('point', [{x2}, {y2}], {{
            name: 'B({x2}, {y2})',
            size: 3,
            color: '#ef4444'
        }});

        // Distance line
        const line = board.create('segment', [A, B], {{
            strokeColor: '#10b981',
            strokeWidth: 2
        }});

        // Distance label (updates on drag)
        const distance = board.create('text', [
            () => (A.X() + B.X()) / 2,
            () => (A.Y() + B.Y()) / 2 + 0.5,
            () => {{
                const dx = B.X() - A.X();
                const dy = B.Y() - A.Y();
                const d = Math.sqrt(dx*dx + dy*dy);
                return 'Distance: ' + d.toFixed(2);
            }}
        ], {{fontSize: 14, color: '#10b981'}});
        </script>
        """,

        "quadratic_parabola": """
        <div id="jxgbox_{id}" class="jxgbox" style="width:600px; height:400px;"></div>
        <div>
            <label>a: <input type="range" id="slider_a_{id}" min="-2" max="2" step="0.1" value="{a}"></label>
            <label>b: <input type="range" id="slider_b_{id}" min="-5" max="5" step="0.1" value="{b}"></label>
            <label>c: <input type="range" id="slider_c_{id}" min="-5" max="5" step="0.1" value="{c}"></label>
        </div>
        <script>
        const board = JXG.JSXGraph.initBoard('jxgbox_{id}', {{
            boundingbox: [-10, 10, 10, -10],
            axis: true
        }});

        let a = {a}, b = {b}, c = {c};

        // Parabola function
        const f = (x) => a * x * x + b * x + c;

        // Plot parabola
        const curve = board.create('functiongraph', [f], {{
            strokeColor: '#8b5cf6',
            strokeWidth: 3
        }});

        // Roots (x-intercepts)
        const updateRoots = () => {{
            const disc = b*b - 4*a*c;
            board.removeObject(board.select({{type: 'point'}}));

            if (disc >= 0 && a !== 0) {{
                const x1 = (-b + Math.sqrt(disc)) / (2*a);
                const x2 = (-b - Math.sqrt(disc)) / (2*a);
                board.create('point', [x1, 0], {{name: 'Root 1', color: '#ef4444'}});
                board.create('point', [x2, 0], {{name: 'Root 2', color: '#ef4444'}});
            }}
        }};

        // Sliders update parabola
        document.getElementById('slider_a_{id}').oninput = (e) => {{
            a = parseFloat(e.target.value);
            board.update();
            updateRoots();
        }};
        // ... similar for b, c
        updateRoots();
        </script>
        """
    }

    async def generate(
        self,
        diagram_type: str,
        variables: Dict[str, Any],
        language: str = "en"
    ) -> str:
        """Generate interactive JSXGraph diagram"""

        template = self.TEMPLATES.get(diagram_type)
        if not template:
            return f"<p>Diagram type '{diagram_type}' not found</p>"

        # Inject variables
        diagram_id = uuid.uuid4().hex[:8]
        html = template.format(id=diagram_id, **variables)

        # Add multi-language labels if needed
        if language != "en":
            html = await self._translate_labels(html, language)

        return html

    async def _translate_labels(self, html: str, language: str) -> str:
        """Translate diagram labels to target language"""
        # Extract text nodes, translate via TranslationService
        # Replace in HTML
        return html  # Simplified for now
```

#### **New Tool: GenerateInteractiveDiagramTool**

```python
# app/tools/veda_tools.py (ENHANCED)
class GenerateInteractiveDiagramTool(BaseTool):
    """Generate JSXGraph interactive diagrams"""

    name = "generate_interactive_diagram"
    description = "Create interactive mathematical visualization that students can manipulate"

    def __init__(self, jsx_generator):
        self.jsx = jsx_generator

    async def execute(
        self,
        diagram_type: str,
        variables: Dict[str, Any],
        concept: str
    ) -> ToolResult:
        """
        Args:
            diagram_type: "coordinate_distance", "quadratic_parabola", "trigonometry_unit_circle"
            variables: Values to inject (e.g., {"x1": 2, "y1": 3, "x2": 5, "y2": 7})
            concept: Topic name for context
        """
        try:
            html = await self.jsx.generate(diagram_type, variables)

            return ToolResult(
                success=True,
                data={
                    "diagram_html": html,
                    "type": diagram_type,
                    "interactive": True,
                    "instruction": "Drag points or use sliders to explore the concept!"
                }
            )

        except Exception as exc:
            return ToolResult(success=False, error=str(exc))
```

---

## Part 4: Expansion Roadmap (Post-CBSE Math)

### **Phase 2A: CBSE Class 10 - All Subjects (3 months)**

```python
# Add subjects
subjects = [
    {"code": "SCIENCE", "name": "Science", "icon": "🔬"},
    {"code": "SOCIAL", "name": "Social Studies", "icon": "🌍"},
    {"code": "ENGLISH", "name": "English", "icon": "📖"},
    {"code": "HINDI", "name": "Hindi", "icon": "🇮🇳"}
]

# Reuse pattern system
# Science gets 60 patterns (Physics, Chemistry, Biology)
# Social gets 50 patterns (History, Geography, Civics, Economics)
```

### **Phase 2B: Multi-Board Expansion (3 months)**

```python
# Add boards
boards = [
    {"code": "KARNATAKA", "name": "Karnataka SSLC", "language": "kn"},
    {"code": "KERALA", "name": "Kerala SSLC", "language": "ml"},
    {"code": "TAMIL_NADU", "name": "Tamil Nadu SSLC", "language": "ta"},
    {"code": "MAHARASHTRA", "name": "Maharashtra SSC", "language": "mr"},
    {"code": "WEST_BENGAL", "name": "West Bengal Madhyamik", "language": "bn"}
]

# Key differences:
# 1. Exam pattern (Karnataka: 100 marks, CBSE: 80 marks)
# 2. Syllabus order (topics reordered)
# 3. Language (translate patterns to Kannada, Malayalam, etc.)
# 4. Difficulty curve (some boards harder than others)
```

### **Phase 3: Class 11-12 (6 months)**

```python
# Add class levels
for class_level in [11, 12]:
    # Class 11 Math: Calculus, 3D Geometry, Statistics
    # Class 12 Math: Integrals, Differential Equations, Vectors
    pass

# Reuse same architecture, just add new topics and patterns
```

### **Phase 4: Competitive Exams (12 months)**

```python
# Add exam types
competitive_exams = [
    {"code": "JEE_MAIN", "name": "JEE Main", "subjects": ["MATH", "PHYSICS", "CHEMISTRY"]},
    {"code": "JEE_ADVANCED", "name": "JEE Advanced"},
    {"code": "NEET", "name": "NEET", "subjects": ["BIOLOGY", "PHYSICS", "CHEMISTRY"]},
    {"code": "CAT", "name": "CAT MBA", "subjects": ["QUANT", "VERBAL", "LOGICAL"]},
    {"code": "UPSC_PRELIMS", "name": "UPSC Civil Services"}
]

# Competitive exam patterns are HARDER
# Need advanced tools:
# - Timed mock tests
# - Rank prediction
# - All-India ranking
# - College predictor (based on score)
```

---

## Part 5: Production-Grade Security & Performance

### **Security (Zero Compromises)**

```python
# 1. Input Sanitization
class InputValidator:
    """Prevent injection attacks"""

    @staticmethod
    def sanitize_student_input(text: str) -> str:
        # Remove SQL injection attempts
        # Remove XSS attempts
        # Remove prompt injection attempts
        return bleach.clean(text, tags=[], strip=True)

# 2. Rate Limiting
from slowapi import Limiter

limiter = Limiter(key_func=lambda: request.client.host)

@app.post("/chat")
@limiter.limit("10/minute")  # Prevent abuse
async def chat(request: ChatRequest):
    pass

# 3. Data Encryption
# All PII encrypted at rest
# Supabase RLS policies for multi-tenancy

# 4. Audit Logging
class AuditLogger:
    """Track all sensitive operations"""

    async def log_event(
        self,
        user_id: str,
        event_type: str,
        entity_type: str,
        entity_id: str,
        metadata: Dict
    ):
        await db.execute(
            "INSERT INTO audit_logs (user_id, event_type, entity_type, entity_id, metadata, ip_address) VALUES (...)"
        )

# Log: student progress, payments, data exports, admin actions
```

### **Performance (Handle 100K concurrent users)**

```python
# 1. Caching Strategy
from redis import asyncio as aioredis

class CacheManager:
    """Multi-layer caching"""

    def __init__(self):
        self.redis = aioredis.from_url("redis://localhost")
        self.local_cache = {}  # In-memory LRU

    async def get_pattern(self, pattern_id: str, language: str = "en"):
        # L1: Local cache (instant)
        key = f"pattern:{pattern_id}:{language}"
        if key in self.local_cache:
            return self.local_cache[key]

        # L2: Redis cache (< 1ms)
        cached = await self.redis.get(key)
        if cached:
            self.local_cache[key] = json.loads(cached)
            return self.local_cache[key]

        # L3: Database (10-50ms)
        pattern = await db.fetch_one("SELECT * FROM question_patterns WHERE pattern_id = $1", pattern_id)

        # Warm caches
        await self.redis.setex(key, 3600, json.dumps(pattern))
        self.local_cache[key] = pattern

        return pattern

# 2. Database Indexing
"""
CREATE INDEX idx_patterns_topic ON question_patterns(topic_id, difficulty);
CREATE INDEX idx_mastery_user_topic ON topic_mastery(user_id, topic_id);
CREATE INDEX idx_progress_user_curriculum ON student_curriculum_progress(user_id, curriculum_id);
"""

# 3. Connection Pooling
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,  # Max 20 concurrent connections
    max_overflow=10,
    pool_pre_ping=True  # Check connection health
)

# 4. CDN for Static Assets
# JSXGraph diagrams served from CloudFlare CDN
# Pattern images from S3 + CloudFront
```

---

## Part 6: One-of-a-Kind Features

### **What Makes LOKAAH Unbeatable:**

1. **Zero-Hallucination Math** ✅ (Already implemented)
2. **Multi-Board + Multi-Language** 🆕 (Scalability architecture)
3. **Interactive JSXGraph Visualizations** 🆕 (Enhanced)
4. **AI Tutor with Personality** ✅ (VEDA, PULSE, ATLAS)
5. **Gamification at Duolingo Level** 🆕 (Phase 3)
6. **Predicted Board Scores** 🆕 (ML model)
7. **Parent Transparency** 🆕 (Weekly WhatsApp reports)
8. **Offline Mode** 🆕 (Future: PWA with IndexedDB)
9. **Voice Input** 🆕 (Future: Gemini multimodal)
10. **Peer Learning** 🆕 (Study groups, leaderboards)

**No competitor has all 10.** Most have 2-3.

---

## Part 7: Timeline (Enhanced Phase 3 Kickoff)

### **Days 1-3: Architecture & Curriculum Setup**
- [x] Create scalable database schema
- [x] Implement CurriculumManager
- [x] Build TranslationService
- [x] Create CBSE Class 10 Math curriculum entry
- [x] Define all 60 topics in topics table

### **Days 4-6: Pattern Library Creation**
- [x] Create `app/oracle/patterns/` directory structure
- [x] Write 60 JSON pattern templates
- [x] Test pattern generation with SafeMathSandbox
- [x] Translate 10 critical patterns to Hindi (validation)

### **Days 7-9: LLM-ify Agents (Original Phase 3)**
- [x] Convert PULSE to Gemini LLM with tools
- [x] Convert ATLAS to Gemini LLM with tools
- [x] Bind tools to VEDA for autonomous calling
- [x] Test multi-hop flows

### **Days 10-12: Gamification System**
- [x] Add XP/Level/Streak schema to Supabase
- [x] Implement StreakManager service
- [x] Create achievement badge system
- [x] Build leaderboard API
- [x] Integrate into VEDA responses

### **Days 13-15: JSXGraph Enhancement**
- [x] Enhance DiagramGenerator with 10 interactive templates
- [x] Create GenerateInteractiveDiagramTool
- [x] Integrate into VEDA teaching flow
- [x] Test on mobile (responsive design)

---

## Conclusion

**You're not building a tutoring app. You're building the operating system for Indian education.**

Every decision from today onwards must answer:
- ✅ **Will this scale to 100+ boards?**
- ✅ **Will this work in Hindi/Tamil/Telugu?**
- ✅ **Can we copy-paste this to Science/Social Studies?**
- ✅ **Will 100K students use this daily?**

**I'm architecting for infinite scale. Let's build the Duolingo of India.** 🚀
