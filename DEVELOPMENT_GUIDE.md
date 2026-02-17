# 🛠️ LOKAAH Development Guide

Complete guide to set up, run, and develop the LOKAAH multi-agent AI tutoring platform.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Setup (Supabase)](#database-setup-supabase)
4. [Running the Development Server](#running-the-development-server)
5. [Testing](#testing)
6. [API Endpoints](#api-endpoints)
7. [Troubleshooting](#troubleshooting)
8. [Development Workflow](#development-workflow)
9. [Optional Features](#optional-features)

---

## Prerequisites

### System Requirements

- **Python**: 3.10 or higher
- **Operating System**: Windows, macOS, or Linux
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 2GB free space

### Required Software

1. **Python 3.10+**
   ```bash
   # Check Python version
   python --version  # Should be 3.10 or higher
   ```

2. **Git** (for version control)
   ```bash
   git --version
   ```

3. **Supabase Account** (for database)
   - Sign up at: https://supabase.com
   - Create a new project

### Optional Software (for full features)

> **Note:** LOKAAH works fully without ffmpeg! All features (VEDA, ORACLE, PULSE, ATLAS, Photo Solver, JSXGraph) work. You only need ffmpeg for Manim math animations.

- **ffmpeg** (for Manim video rendering) - **OPTIONAL**
  - **Windows**: See detailed guide → [INSTALL_FFMPEG.md](INSTALL_FFMPEG.md)
  - **Quick Windows install**: Download from https://www.gyan.dev/ffmpeg/builds/ (no admin needed)
  - **macOS**: `brew install ffmpeg`
  - **Linux**: `sudo apt-get install ffmpeg`

- **LaTeX** (for Manim math formulas) - **OPTIONAL**
  - Only needed if you install ffmpeg + Manim
  - Windows: Install MiKTeX from https://miktex.org/
  - macOS: `brew install --cask mactex`
  - Linux: `sudo apt-get install texlive-full`

---

## Environment Setup

### 1. Clone the Repository

```bash
cd c:/Users/Lenovo
git clone <your-repo-url> lokaah_app
cd lokaah_app
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment

# Windows (bash/Git Bash)
source venv/Scripts/activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Install Manim (optional - for animations)
pip install manim

# Verify installation
python -c "import fastapi, supabase, google.genai; print('✅ All dependencies installed')"
```

### 4. Configure Environment Variables

Create `.env` file in project root:

```bash
# Copy example
cp .env.example .env

# Edit .env with your credentials
```

`.env` file contents:

```env
# ==========================================
# APPLICATION SETTINGS
# ==========================================
APP_NAME=LOKAAH
ENV=development  # development | production
DEBUG=true
PORT=8000

# ==========================================
# GEMINI AI (Required)
# ==========================================
# Get API key from: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# Optional: Use Vertex AI instead of API key
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
# GOOGLE_CLOUD_PROJECT=your-project-id
# GOOGLE_CLOUD_LOCATION=us-central1

# ==========================================
# SUPABASE DATABASE (Required)
# ==========================================
# Get credentials from: https://supabase.com/dashboard/project/<project-id>/settings/api
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here

# ==========================================
# SECURITY
# ==========================================
# IMPORTANT: In production, set specific origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
# For production: https://yourdomain.com,https://app.yourdomain.com

# ==========================================
# AI CONFIGURATION
# ==========================================
# Ratio of AI-generated vs database questions (0.0 to 1.0)
AI_RATIO=0.5

# ==========================================
# RATE LIMITING
# ==========================================
RATE_LIMIT_MAX_REQUESTS=30
RATE_LIMIT_WINDOW_SECONDS=60
```

**Important:** Replace the following:
- `your_gemini_api_key_here` - Get from [Google AI Studio](https://aistudio.google.com/app/apikey)
- `your-project.supabase.co` - Your Supabase project URL
- `your_supabase_anon_key_here` - Your Supabase anon/public key

---

## Database Setup (Supabase)

### 1. Create Supabase Project

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Click "New Project"
3. Choose organization and set:
   - Project name: `lokaah-app`
   - Database password: (save this securely)
   - Region: Choose closest to you

### 2. Run Database Migrations

Navigate to SQL Editor in Supabase dashboard and run migrations in order:

**Migration 1: Core Tables** (`supabase/migrations/001_core_tables.sql`)

```sql
-- Run the SQL from 001_core_tables.sql
-- Creates: learning_sessions, student_attempts, etc.
```

**Migration 2: Agentic Memory** (`supabase/migrations/002_agentic_memory.sql`)

```sql
-- Run the SQL from 002_agentic_memory.sql
-- Creates: conversation_history, session_summaries, concept_mastery, concept_attempts
```

**Migration 3: Photo Solver** (`supabase/migrations/003_photo_solver.sql`)

```sql
-- Run the SQL from 003_photo_solver.sql
-- Creates: solved_questions table for photo upload feature
```

### 3. Verify Database Setup

```bash
# Test database connection
python -c "from app.core.database import get_db; db = get_db(); print('✅ Database connected')"
```

---

## Running the Development Server

### Start Server

```bash
# Make sure virtual environment is activated
source venv/Scripts/activate  # Windows Git Bash
# source venv/bin/activate  # macOS/Linux

# Start development server with auto-reload
python main.py
```

Expected output:
```
=== LOKAAH AI Tutoring Platform ===
Environment: development
Debug Mode: True
Gemini Available: True
Database: Connected
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Access the Server

- **API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

### Stop Server

Press `CTRL+C` in the terminal

---

## Testing

### Manual Testing

**1. Health Check**

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "oracle_engine": "ready"
}
```

**2. Chat with VEDA (Teaching Agent)**

Create test file: `test_veda_chat.json`
```json
{
  "message": "Explain quadratic equations to me",
  "session_id": "test_session_1",
  "user_profile": {
    "language_preference": "english"
  }
}
```

Test:
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d @test_veda_chat.json
```

**3. Chat with PULSE (Mental Health Agent)**

```json
{
  "message": "I feel stressed about my exams",
  "session_id": "test_session_2"
}
```

**4. Chat with ATLAS (Study Planner)**

```json
{
  "message": "Help me create a study plan for board exams",
  "session_id": "test_session_3"
}
```

**5. Test Photo Solver** (upload image of question)

```bash
# Upload image file
curl -X POST "http://localhost:8000/api/v1/photo/solve?subject=mathematics" \
  -F "image=@question_image.jpg"
```

**6. Test Manim Animations**

```bash
# Generate quadratic formula animation
curl -X POST "http://localhost:8000/api/v1/animation/generate?concept=quadratic_formula&quality=medium_quality"

# Download generated video
curl -O http://localhost:8000/api/v1/animation/serve/quadratic_formula
```

### Automated Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_agents.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

---

## API Endpoints

### Core Chat Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/chat` | POST | Multi-agent chat (supervisor routes) |
| `/api/v1/chat/stream` | POST | Streaming chat (SSE) |
| `/api/v1/stats` | GET | System statistics |

### VEDA Endpoints (Teaching)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/veda/chat` | POST | Direct VEDA interaction |

### ORACLE Endpoints (Assessment)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/question/generate` | POST | Generate practice question |
| `/api/v1/attempt/submit` | POST | Submit answer for grading |
| `/api/v1/exam/generate` | POST | Generate full exam |

### Photo Solver Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/photo/solve` | POST | Solve question from image |
| `/api/v1/photo/subjects` | GET | List supported subjects |
| `/api/v1/photo/history/{session_id}` | GET | Get solved photo history |

### Manim Animation Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/animation/generate` | POST | Generate math animation |
| `/api/v1/animation/list` | GET | List available concepts |
| `/api/v1/animation/serve/{concept}` | GET | Download video file |

### Session Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/session/start` | POST | Start new learning session |
| `/api/v1/session/{session_id}/status` | GET | Get session status |

---

## Troubleshooting

### Common Issues

**1. "ModuleNotFoundError: No module named 'google.genai'"**

```bash
# Install Google Generative AI SDK
pip install google-generativeai
```

**2. "Gemini API key not configured"**

- Check `.env` file has `GEMINI_API_KEY=...`
- Get API key from: https://aistudio.google.com/app/apikey
- Restart server after adding key

**3. "Database connection failed"**

- Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Check Supabase project is active
- Run migrations in Supabase SQL Editor

**4. "Port 8000 already in use"**

```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# macOS/Linux:
lsof -i :8000
kill -9 <process_id>

# Or change port in .env
PORT=8001
```

**5. "Manim not found"**

```bash
# Install Manim
pip install manim

# Install system dependencies
# Windows: Install ffmpeg and MiKTeX
# macOS: brew install ffmpeg && brew install --cask mactex
# Linux: sudo apt-get install ffmpeg texlive-full
```

**6. "Rate limit exceeded"**

- Wait 60 seconds (default rate limit window)
- Or increase `RATE_LIMIT_MAX_REQUESTS` in `.env`

### Debugging

**Enable verbose logging:**

```bash
# In .env
DEBUG=true

# Check logs in terminal
```

**Test individual components:**

```python
# Test Gemini connection
python -c "from app.agents.veda import VEDAAdapter; v = VEDAAdapter(); print('✅ VEDA ready')"

# Test Supabase connection
python -c "from app.core.database import get_db; db = get_db(); print('✅ DB connected')"
```

---

## Development Workflow

### Project Structure

```
lokaah_app/
├── app/
│   ├── agents/          # AI agents (VEDA, ORACLE, PULSE, ATLAS, SPARK)
│   ├── api/             # FastAPI endpoints
│   ├── core/            # Config, database, utils
│   ├── graph/           # LangGraph workflow (multi-agent routing)
│   ├── models/          # Pydantic schemas
│   ├── oracle/          # Hybrid orchestrator (AI + DB questions)
│   ├── services/        # Services (Manim, Photo Solver, Error Analyzer, etc.)
│   └── tools/           # Agentic tools (for Phase 4)
├── supabase/
│   └── migrations/      # SQL migrations
├── tests/               # Automated tests
├── .env                 # Environment variables (DO NOT COMMIT)
├── .gitignore           # Git ignore rules
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
└── DEVELOPMENT_GUIDE.md # This file
```

### Making Changes

1. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**
   - Edit code
   - Add tests if applicable

3. **Test locally**
   ```bash
   # Run development server
   python main.py

   # Run tests
   pytest tests/ -v
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Review changes
   - Merge to main

### Code Style

- **Python**: Follow PEP 8
- **Type hints**: Use for all function parameters and returns
- **Docstrings**: Use for all public functions and classes
- **Imports**: Sort with `isort` or manually group (stdlib, third-party, local)

---

## Optional Features

### 1. Enable JSXGraph Integration

JSXGraph is already integrated for interactive math visualizations. To use:

```python
# In VEDA agent
from app.services.diagram_generator import DiagramGenerator

diagram_gen = DiagramGenerator()
jsxgraph_code = diagram_gen.generate_interactive_graph(concept="parabola")
```

### 2. Enable Manim Animations

```bash
# Install Manim
pip install manim

# Install system dependencies
# See prerequisites section above

# Generate animation
curl -X POST "http://localhost:8000/api/v1/animation/generate?concept=pythagoras_theorem"
```

### 3. Enable Photo Math for All Subjects

Already implemented! Upload any question image:

```bash
curl -X POST "http://localhost:8000/api/v1/photo/solve?subject=mathematics" \
  -F "image=@question.jpg"
```

Supported subjects:
- mathematics
- physics
- chemistry
- biology
- social_science
- english

### 4. Enable Voice Input/Output (Future)

- Integrate with Web Speech API on frontend
- Convert audio → text → VEDA → text → audio

### 5. Persistent Memory (Supabase)

Already implemented! All conversations are stored in:
- `conversation_history` table
- `session_summaries` table (auto-summarizes every 10 turns)
- `concept_mastery` table (Bayesian Knowledge Tracing)

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Set `ENV=production` in `.env`
- [ ] Set `DEBUG=false` in `.env`
- [ ] Configure HTTPS reverse proxy (nginx/Caddy)
- [ ] Update `CORS_ORIGINS` to production domains only
- [ ] Set up authentication (JWT or Supabase Auth)
- [ ] Configure rate limiting for production scale
- [ ] Set up monitoring (Sentry, Datadog, etc.)
- [ ] Configure CDN for Manim videos (S3, Cloudflare R2)
- [ ] Run load tests

### Deployment Commands

```bash
# Install production dependencies only
pip install -r requirements.txt --no-dev

# Run with production server (gunicorn)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or use uvicorn with multiple workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --no-access-log
```

---

## Getting Help

- **Issues**: Open an issue on GitHub
- **Documentation**: Check API docs at `/docs`
- **Logs**: Check terminal output when `DEBUG=true`

---

## Quick Reference

**Start dev server:**
```bash
source venv/Scripts/activate  # Activate venv
python main.py                 # Start server
```

**Test API:**
```bash
curl http://localhost:8000/api/v1/health
```

**Run tests:**
```bash
pytest tests/ -v
```

**Access docs:**
```
http://localhost:8000/docs
```

---

**Happy Developing! 🚀**

For more details, see [ENHANCEMENTS_COMPLETE.md](ENHANCEMENTS_COMPLETE.md) for full feature list and architecture overview.
