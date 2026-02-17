# ⚡ Quick Start - Common Commands

Quick reference for daily development tasks.

---

## 🚀 Starting the Server

```bash
# 1. Navigate to project
cd c:/Users/Lenovo/lokaah_app

# 2. Activate virtual environment (do this EVERY TIME you open a new terminal)
source venv/Scripts/activate

# 3. Start server
python main.py
```

**Expected output:**
```
=== LOKAAH AI Tutoring Platform ===
Environment: development
Debug Mode: True
Gemini Available: True
Database: Connected
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ Server is running!

**Access API docs:** http://localhost:8000/docs

---

## 🛑 Stopping the Server

In the terminal where server is running:

**Press:** `CTRL + C`

---

## 🧪 Quick Tests

### Test 1: Health Check

```bash
curl http://localhost:8000/api/v1/health
```

### Test 2: Chat (English)

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain Pythagoras theorem", "session_id": "test1"}'
```

### Test 3: Chat (Hinglish)

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Pythagoras theorem batao", "session_id": "test2", "user_profile": {"language_preference": "hinglish"}}'
```

### Test 4: Generate Animation

```bash
curl -X POST "http://localhost:8000/api/v1/animation/generate?concept=quadratic_formula"
```

Then download:

```bash
curl -O http://localhost:8000/api/v1/animation/serve/quadratic_formula
```

### Test 5: Photo Solver

```bash
curl -X POST "http://localhost:8000/api/v1/photo/solve?subject=mathematics" \
  -F "image=@path/to/question.jpg"
```

---

## 📦 Installing New Packages

```bash
# Activate venv first
source venv/Scripts/activate

# Install package
pip install package_name

# Add to requirements.txt
pip freeze > requirements.txt
```

---

## 🔄 Git Commands (After Making Changes)

### Save changes to Git

```bash
# Check what changed
git status

# Add all changes
git add .

# Commit with message
git commit -m "Describe what you changed"

# Push to GitHub (if you set it up)
git push
```

### See what changed

```bash
# See differences
git diff

# See recent commits
git log --oneline -5
```

---

## 🗄️ Database Commands

### View Database in Browser

1. Go to: https://supabase.com/dashboard
2. Click your project
3. Click "Table Editor"

### Run SQL Query

1. Click "SQL Editor"
2. Click "New Query"
3. Paste SQL
4. Click "Run"

---

## 🐛 Debugging

### View Logs

Logs appear in the terminal where server is running.

### Enable More Verbose Logs

In `.env`:

```env
DEBUG=true
```

Restart server.

### Test Individual Components

```python
# Test Gemini connection
python -c "from app.agents.veda import VEDAAdapter; v = VEDAAdapter(); print('VEDA ready')"

# Test Database connection
python -c "from app.core.database import get_db; db = get_db(); print('DB connected')"

# Test Photo Solver
python -c "from app.services.photo_solver import get_photo_solver; ps = get_photo_solver(); print('Photo Solver ready')"
```

---

## 🎨 Testing Manim Locally (Without API)

```bash
# Navigate to output directory
cd c:/Users/Lenovo/lokaah_app

# Render a single animation
manim -pql app/services/manim_generator.py QuadraticFormula
```

Flags:
- `-p` = preview (auto-open video)
- `-q` = quality (l=low, m=medium, h=high)

---

## 📱 Frontend Connection (When You Build It)

Your frontend should call:

**Chat:**
```javascript
fetch('http://localhost:8000/api/v1/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    message: "Explain quadratic equations",
    session_id: "user123",
    user_profile: {language_preference: "english"}
  })
})
```

**Photo Upload:**
```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);

fetch('http://localhost:8000/api/v1/photo/solve?subject=mathematics', {
  method: 'POST',
  body: formData
})
```

---

## 🚨 Emergency Fixes

### Server won't start

```bash
# Kill any process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Then try again
python main.py
```

### Packages messed up

```bash
# Delete and recreate venv
rm -rf venv
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

### Database issues

1. Check Supabase dashboard is accessible
2. Verify `.env` has correct URL and keys
3. Re-run migrations if needed

---

## 📊 Project Structure (Where Everything Is)

```
lokaah_app/
├── app/
│   ├── agents/              # AI agents (VEDA, ORACLE, PULSE, ATLAS, SPARK)
│   │   ├── veda.py         # Teaching agent
│   │   ├── pulse.py        # Mental health agent
│   │   ├── atlas.py        # Study planner
│   │   └── ...
│   ├── api/
│   │   └── endpoints.py    # All API routes (add new endpoints here)
│   ├── services/
│   │   ├── manim_generator.py      # Animations (add more concepts here)
│   │   ├── photo_solver.py         # Photo Math
│   │   ├── error_analyzer.py       # Error Pattern DNA
│   │   └── knowledge_tracer.py     # Bayesian mastery tracking
│   ├── graph/               # LangGraph workflow (multi-agent routing)
│   └── tools/               # Agentic tools
├── supabase/
│   └── migrations/          # Database schemas
├── .env                     # YOUR SECRETS (never upload!)
├── main.py                  # START HERE - run this file
└── requirements.txt         # Python packages list
```

---

## 🎯 Common Tasks

### Add a new Manim animation

1. Edit `app/services/manim_generator.py`
2. Add to `CONCEPT_TEMPLATES` dict
3. Test: `curl -X POST "http://localhost:8000/api/v1/animation/generate?concept=YOUR_CONCEPT"`

### Add a new API endpoint

1. Edit `app/api/endpoints.py`
2. Add `@router.post("/your-endpoint")`
3. Test in Swagger UI: http://localhost:8000/docs

### Change how VEDA teaches

1. Edit `app/agents/veda.py`
2. Modify system prompts or teaching logic
3. Restart server
4. Test

---

## 🌐 Available Languages

Pass in `user_profile.language_preference`:

- `english` (default)
- `hinglish` (Hindi + English)
- `tanglish` (Tamil + English)
- `tenglish` (Telugu + English)
- `kanglish` (Kannada + English)
- `manglish` (Malayalam + English)
- `benglish` (Bengali + English)
- `marathglish` (Marathi + English)
- `gujarlish` (Gujarati + English)

---

## 📞 Need Help?

1. **Setup issues:** Check [SETUP_GUIDE_BEGINNERS.md](SETUP_GUIDE_BEGINNERS.md)
2. **Technical details:** Check [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)
3. **Latest features:** Check [LATEST_UPDATES.md](LATEST_UPDATES.md)
4. **Error messages:** Google the exact error, or check logs

---

**Keep this file open while developing! 📌**
