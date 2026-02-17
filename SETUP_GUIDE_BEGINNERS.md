# 🎓 LOKAAH - Complete Setup Guide for Beginners

This guide explains everything in **plain English** with **step-by-step instructions**. No technical jargon!

---

## 📋 Table of Contents

1. [Understanding What LOKAAH Does](#understanding-what-lokaah-does)
2. [Installing Required Software (Windows)](#installing-required-software-windows)
3. [Setting Up Git Repository](#setting-up-git-repository)
4. [Installing Python Dependencies](#installing-python-dependencies)
5. [Setting Up Database](#setting-up-database)
6. [Running Your First Test](#running-your-first-test)
7. [How Manim and JSXGraph Work](#how-manim-and-jsxgraph-work)
8. [How Students Learn in LOKAAH](#how-students-learn-in-lokaah)
9. [Testing All Features](#testing-all-features)
10. [Troubleshooting Common Issues](#troubleshooting-common-issues)

---

## 🎯 Understanding What LOKAAH Does

**LOKAAH is an AI tutor that helps CBSE Class 10 students learn Math (and other subjects).**

Think of it as having 5 different teachers, each with a special role:

1. **VEDA** 🧠 - The teaching expert (explains concepts using Socratic method)
2. **ORACLE** 📝 - The quiz master (generates practice questions, grades answers)
3. **PULSE** ❤️ - The counselor (handles stress, anxiety, motivation)
4. **ATLAS** 📅 - The study planner (creates study schedules, prioritizes topics)
5. **SPARK** 💡 - The researcher (finds learning resources)

**Special Features:**
- **Photo Math**: Take a picture of ANY question (Math, Physics, Chemistry, etc.) → Get instant solution
- **Manim Animations**: Watch beautiful animated explanations of concepts (like parabola movement, Pythagoras theorem)
- **JSXGraph**: Interactive graphs students can drag and play with
- **9 Languages**: English, Hinglish, Tanglish, Telugu-English, etc.
- **Smart Learning**: Tracks what student knows, what they struggle with

---

## 💻 Installing Required Software (Windows)

### Step 1: Python 3.10 or Higher

**Check if you already have Python:**

```bash
python --version
```

If it shows `Python 3.10` or higher, **you're good! Skip to Step 2.**

If not, download Python:

1. Go to: https://www.python.org/downloads/
2. Click "Download Python 3.12.x" (latest version)
3. **IMPORTANT**: When installing, check ✅ "Add Python to PATH"
4. Click "Install Now"
5. Wait for installation to finish

**Verify installation:**

```bash
python --version
# Should show: Python 3.12.x
```

---

### Step 2: Git (Version Control)

**Check if you have Git:**

```bash
git --version
```

If it works, **skip to Step 3.**

If not, install Git:

1. Go to: https://git-scm.com/download/win
2. Download "64-bit Git for Windows Setup"
3. Run the installer
4. **Accept all default options** (just keep clicking Next)
5. Finish installation

**Verify installation:**

```bash
git --version
# Should show: git version 2.x.x
```

---

### Step 3: ffmpeg (For Manim Video Rendering)

**What is ffmpeg?** It's a tool that creates video files from animations.

**DETAILED INSTALLATION STEPS FOR WINDOWS:**

#### Option A: Using Chocolatey (Easiest - Recommended)

1. **Install Chocolatey first** (Windows package manager)

   Open PowerShell **as Administrator** (right-click PowerShell → Run as Administrator):

   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```

   Wait for installation to finish.

2. **Install ffmpeg using Chocolatey:**

   ```powershell
   choco install ffmpeg
   ```

   Type `y` when asked to confirm.

3. **Close and reopen PowerShell/Git Bash**

4. **Verify installation:**

   ```bash
   ffmpeg -version
   # Should show: ffmpeg version x.x.x
   ```

   ✅ **Done! ffmpeg is installed and ready.**

#### Option B: Manual Installation (If Chocolatey doesn't work)

1. **Download ffmpeg:**
   - Go to: https://www.gyan.dev/ffmpeg/builds/
   - Click "ffmpeg-release-essentials.zip" (about 80MB)
   - Download will start

2. **Extract the ZIP file:**
   - Right-click the downloaded ZIP → "Extract All"
   - Choose location: `C:\ffmpeg`
   - Click "Extract"

3. **Add to Windows PATH** (so Windows can find ffmpeg):

   a. Open File Explorer

   b. Right-click "This PC" → Properties

   c. Click "Advanced system settings" (on the right side)

   d. Click "Environment Variables" button

   e. Under "System variables", find "Path" → Click "Edit"

   f. Click "New"

   g. Type: `C:\ffmpeg\bin`

   h. Click "OK" on all windows

   i. **Close and reopen any terminal/PowerShell windows**

4. **Verify installation:**

   ```bash
   ffmpeg -version
   # Should show: ffmpeg version x.x.x
   ```

   ✅ **Done! ffmpeg is installed.**

---

### Step 4: LaTeX (For Math Formulas in Manim)

**What is LaTeX?** It's a tool that creates beautiful mathematical formulas (like x = (-b ± √(b²-4ac))/2a).

**INSTALLATION STEPS:**

1. **Download MiKTeX:**
   - Go to: https://miktex.org/download
   - Click "Download" under "Windows"
   - File is large (about 200MB), wait for download

2. **Install MiKTeX:**
   - Run the downloaded `.exe` file
   - Choose "Install MiKTeX for all users" (recommended)
   - Installation path: Leave as default (`C:\Program Files\MiKTeX`)
   - Paper size: A4
   - Install missing packages: **Choose "Yes"** (important!)
   - Click "Start" to begin installation
   - Wait 10-15 minutes (it's a big installation)

3. **Verify installation:**

   Close and reopen terminal, then:

   ```bash
   latex --version
   # Should show: MiKTeX-TeX x.x.x
   ```

   ✅ **Done! LaTeX is installed.**

---

## 🗂️ Setting Up Git Repository

Since you haven't added this project to GitHub yet, let's set it up properly.

### Step 1: Initialize Git in Your Project

Open Git Bash or PowerShell, navigate to your project:

```bash
cd c:/Users/Lenovo/lokaah_app
```

Initialize Git:

```bash
git init
```

You'll see: `Initialized empty Git repository in c:/Users/Lenovo/lokaah_app/.git/`

✅ **Git is now tracking this folder.**

---

### Step 2: Verify .gitignore is Correct

The `.gitignore` file tells Git which files to **ignore** (not upload to GitHub).

**CRITICAL:** We don't want to upload `.env` (it has your secret API keys!) or other sensitive files.

Your `.gitignore` is already set up correctly! It includes:
- `.env` (your secrets - NEVER upload this!)
- `__pycache__/` (Python temporary files)
- `venv/` (your virtual environment - too large to upload)

You can verify:

```bash
cat .gitignore
# Should show .env, __pycache__, venv/, etc.
```

✅ **Gitignore is correct.**

---

### Step 3: Make Your First Commit

A "commit" is like taking a snapshot of your code at this moment.

```bash
# Check what files will be added
git status

# Add all files (except those in .gitignore)
git add .

# Create your first commit
git commit -m "Initial commit - LOKAAH AI Tutoring Platform"
```

You'll see a message showing files were committed.

✅ **First commit created!**

---

### Step 4: Create GitHub Repository (Optional)

If you want to backup your code on GitHub:

1. **Go to GitHub:** https://github.com
2. **Sign in** (or create account if you don't have one)
3. **Click the "+" icon** (top right) → "New repository"
4. **Repository name:** `lokaah-app`
5. **Description:** "AI-powered adaptive learning platform for CBSE students"
6. **Visibility:** Choose "Private" (your code stays secret)
7. **DON'T check** "Initialize with README" (we already have code)
8. **Click "Create repository"**

GitHub will show you commands. **Copy the commands under "push an existing repository":**

```bash
git remote add origin https://github.com/YOUR_USERNAME/lokaah-app.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

Enter your GitHub password when prompted.

✅ **Code is now on GitHub!**

**To update GitHub later:**

```bash
# After making changes
git add .
git commit -m "Description of what you changed"
git push
```

---

## 📦 Installing Python Dependencies

### Step 1: Create Virtual Environment

A "virtual environment" is like a separate Python installation just for this project. It keeps things clean.

```bash
cd c:/Users/Lenovo/lokaah_app

# Create virtual environment
python -m venv venv
```

Wait 1-2 minutes. A folder called `venv` will appear.

---

### Step 2: Activate Virtual Environment

**Windows Git Bash:**

```bash
source venv/Scripts/activate
```

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

**Windows CMD:**

```cmd
venv\Scripts\activate.bat
```

You'll see `(venv)` appear at the start of your terminal line. This means it's active!

Example:
```
(venv) user@computer:~/lokaah_app$
```

✅ **Virtual environment is active.**

**IMPORTANT:** Always activate the virtual environment before working on the project!

---

### Step 3: Install All Dependencies

Now install all the Python packages needed:

```bash
pip install --upgrade pip

pip install -r requirements.txt
```

This will take 2-5 minutes. You'll see many packages being installed.

---

### Step 4: Install Manim (For Animations)

```bash
pip install manim
```

Wait 1-2 minutes.

**Verify installation:**

```bash
manim --version
# Should show: Manim Community v0.x.x
```

✅ **All Python packages installed!**

---

## 🗄️ Setting Up Database

You already have Supabase credentials in your `.env` file! Let's set up the database tables.

### Step 1: Fix .env for Development

Your `.env` currently has `ENV=production`. Change it to development while testing:

```bash
# Open .env file in Notepad
notepad .env
```

**Change these lines:**

```env
# OLD:
ENV=production
DEBUG=false

# NEW:
ENV=development
DEBUG=true
```

Save and close.

✅ **Environment set to development mode.**

---

### Step 2: Run Database Migrations

Open Supabase dashboard in your browser:

1. Go to: https://supabase.com/dashboard
2. Sign in
3. Click on your project: `lokaah-app` (or whatever you named it)
4. Click "SQL Editor" (left sidebar)

Now run each migration file **one by one**:

#### Migration 1: Core Tables

Click "New Query" and copy-paste the entire contents of:
`c:\Users\Lenovo\lokaah_app\supabase\migrations\001_core_tables.sql`

(If this file doesn't exist, that's okay - it might not be needed)

Click "Run" (bottom right).

Wait for "Success" message.

#### Migration 2: Agentic Memory

Click "New Query" again and copy-paste:
`c:\Users\Lenovo\lokaah_app\supabase\migrations\002_agentic_memory.sql`

Click "Run".

Wait for "Success".

#### Migration 3: Photo Solver

Click "New Query" again and copy-paste:
`c:\Users\Lenovo\lokaah_app\supabase\migrations\003_photo_solver.sql`

Click "Run".

Wait for "Success".

---

### Step 3: Verify Database Setup

In Supabase dashboard:

1. Click "Table Editor" (left sidebar)
2. You should see these tables:
   - `conversation_history`
   - `session_summaries`
   - `concept_mastery`
   - `concept_attempts`
   - `solved_questions`
   - And others

✅ **Database is set up!**

---

## 🚀 Running Your First Test

### Step 1: Start the Server

In Git Bash (with virtual environment activated):

```bash
cd c:/Users/Lenovo/lokaah_app

# Activate venv if not already active
source venv/Scripts/activate

# Start server
python main.py
```

You should see:

```
=== LOKAAH AI Tutoring Platform ===
Environment: development
Debug Mode: True
Gemini Available: True
Database: Connected
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete.
```

✅ **Server is running!**

**Keep this terminal open. Don't close it.**

---

### Step 2: Test in Browser

Open your web browser and go to:

**http://localhost:8000/docs**

You'll see a beautiful interactive API documentation page (Swagger UI).

This shows all the endpoints (features) you can test.

---

### Step 3: Test Health Check

In Swagger UI:

1. Find "GET /api/v1/health"
2. Click on it to expand
3. Click "Try it out"
4. Click "Execute"

You should see:

```json
{
  "status": "healthy",
  "database": "connected",
  "oracle_engine": "ready"
}
```

✅ **Server is working!**

---

## 🎨 How Manim and JSXGraph Work

Let me explain in plain English how these visual tools help students learn:

### What is Manim?

**Manim** is the tool that creates **animated videos** explaining math concepts.

**Example: Pythagoras Theorem**

Instead of just text explanation, student sees:
1. A right-angled triangle appears
2. Sides are labeled a, b, c
3. Squares grow on each side
4. Formula appears: a² + b² = c²
5. Animation shows why it works

**Think of it like those 3Blue1Brown YouTube videos** - super engaging!

**How it works in LOKAAH:**

1. VEDA (teaching agent) explains: "Let me show you Pythagoras theorem"
2. VEDA calls Manim service: "Generate pythagoras_theorem video"
3. Manim creates a beautiful MP4 video (takes 30-60 seconds first time)
4. Video is saved in a folder
5. Next time someone asks, video is instantly available (cached!)
6. Student downloads/watches the video

**What happens behind the scenes:**

```
Student asks: "Explain Pythagoras theorem"
    ↓
VEDA: "Let me show you an animation"
    ↓
Manim Generator:
    - Reads Python code template for Pythagoras
    - Runs ffmpeg to render video frame-by-frame
    - Uses LaTeX to write beautiful math formulas
    - Creates MP4 file
    ↓
Video saved at: c:\Users\Lenovo\lokaah_app\media\pythagoras_theorem.mp4
    ↓
Student watches animation and understands concept!
```

**Pre-defined animations we have:**
- Quadratic Formula
- Pythagoras Theorem
- Linear Equations (y = mx + c graph)
- Area of Circle

**You can add more** by editing templates in `app/services/manim_generator.py`

---

### What is JSXGraph?

**JSXGraph** creates **interactive graphs** that students can play with.

**Example: Parabola (y = x²)**

Instead of static image, student gets:
1. A graph they can see in their browser
2. They can drag points and see parabola change shape
3. They can change formula and see real-time updates
4. Everything is interactive!

**How it works in LOKAAH:**

1. ORACLE generates a question: "Plot y = 2x² + 3x - 5"
2. DiagramGenerator creates JSXGraph code
3. Code is sent to student's browser
4. Browser renders interactive graph using JavaScript
5. Student can drag points, zoom, pan

**Think of it like Desmos calculator** - but built into LOKAAH!

**Example JSXGraph code:**

```javascript
// Create board (canvas for graph)
var board = JXG.JSGraph.initBoard('box', {
    boundingbox: [-5, 10, 5, -5],
    axis: true
});

// Draw parabola
board.create('functiongraph', [function(x) {
    return x*x - 4;
}]);
```

Student sees this in their browser as a beautiful interactive graph!

---

### Manim vs JSXGraph - What's the Difference?

| Feature | Manim | JSXGraph |
|---------|-------|----------|
| **Output** | Video (MP4 file) | Interactive HTML/JavaScript |
| **Usage** | Explaining concepts | Practice & exploration |
| **Example** | "Watch how quadratic formula works" | "Draw your own parabola" |
| **Speed** | Slow (30-60s first time, instant after) | Instant (runs in browser) |
| **Interactivity** | Watch-only | Fully interactive |
| **Best for** | Teaching new concepts | Practicing with graphs |

**Together, they're powerful:**
1. VEDA uses **Manim** to teach concept (video explanation)
2. ORACLE uses **JSXGraph** to let student practice (interactive problems)

---

## 📚 How Students Learn in LOKAAH (Structured Learning)

### Is Learning Structured? YES!

LOKAAH has a **3-level hierarchy** for organized learning:

```
Board (e.g., CBSE)
  └─ Subject (e.g., Mathematics)
      └─ Class (e.g., Class 10)
          └─ Chapters (e.g., Quadratic Equations)
              └─ Sections (e.g., Standard Form)
                  └─ Subsections (e.g., Discriminant)
```

### Example: CBSE Class 10 Math Structure

**Chapter 1: Quadratic Equations**
- Section 1.1: Introduction
  - Subsection: Standard form (ax² + bx + c = 0)
  - Subsection: Roots of quadratic equation
- Section 1.2: Solving Methods
  - Subsection: Factorization
  - Subsection: Completing the square
  - Subsection: Quadratic formula
  - Subsection: Nature of roots (Discriminant)
- Section 1.3: Applications
  - Subsection: Word problems
  - Subsection: Real-life applications

**Chapter 2: Polynomials**
- Section 2.1: Degree of polynomial
- Section 2.2: Zeros of polynomial
- Section 2.3: Division algorithm
- ... and so on

### How Difficulty Increases

Each topic has:
- **Difficulty score** (0.0 to 1.0)
  - 0.0-0.3 = Easy (basic understanding)
  - 0.4-0.6 = Medium (application)
  - 0.7-1.0 = Hard (complex problem-solving)

**ORACLE automatically adjusts difficulty** based on student performance:
- Student answers correctly → Difficulty increases
- Student struggles → Difficulty decreases

### Bayesian Knowledge Tracing

LOKAAH tracks **true mastery**, not just "% correct".

**Example:**
- Student A: Got 8/10 questions correct, but guessed on 6 of them → Mastery: 40%
- Student B: Got 6/10 questions correct, but showed deep understanding → Mastery: 70%

System accounts for:
- **Guessing** (got lucky)
- **Slips** (knew the answer but made careless mistake)
- **Learning** (improves over time)

### Error Pattern DNA

System tracks **7 types of errors**:

1. **Sign Error** - Changed + to - (or vice versa)
2. **Formula Swap** - Used wrong formula
3. **Arithmetic Slip** - Calculation mistake (7×8 = 54 instead of 56)
4. **Concept Gap** - Fundamental misunderstanding
5. **Incomplete Answer** - Stopped before final answer
6. **Unit Mismatch** - Forgot units or conversions
7. **Misread Question** - Solved wrong problem

**Why this matters:**

Instead of "Wrong answer, try again", student gets:
"You often make sign errors. Before solving, circle every + and - in the problem."

**This is unique!** No other EdTech platform does this level of error analysis.

---

## 🧪 Testing All Features

### Test 1: Chat with VEDA (English Default)

Open a new Git Bash window (keep server running in other window):

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain Pythagoras theorem to me",
    "session_id": "test_eng_1"
  }'
```

**Expected:** Response in English (default language)

---

### Test 2: Chat in Hinglish

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Pythagoras theorem samjhao",
    "session_id": "test_hing_1",
    "user_profile": {"language_preference": "hinglish"}
  }'
```

**Expected:** Response in Hinglish (Hindi + English mix)

---

### Test 3: Generate Manim Animation

**Method 1: Using curl**

```bash
curl -X POST "http://localhost:8000/api/v1/animation/generate?concept=quadratic_formula&quality=medium_quality"
```

Wait 30-60 seconds for first generation.

**Method 2: Using browser**

Go to: http://localhost:8000/docs

1. Find "POST /api/v1/animation/generate"
2. Click "Try it out"
3. Set:
   - concept: `quadratic_formula`
   - quality: `medium_quality`
4. Click "Execute"

**Download the video:**

http://localhost:8000/api/v1/animation/serve/quadratic_formula

Save the MP4 file and play it!

---

### Test 4: Photo Math (Take Picture of Question)

**You need an actual image file for this test.**

1. Take a photo of ANY question from your textbook (Math, Physics, Chemistry, etc.)
2. Save it as `question.jpg`

```bash
curl -X POST "http://localhost:8000/api/v1/photo/solve?subject=mathematics" \
  -F "image=@c:/Users/Lenovo/Downloads/question.jpg"
```

Replace the path with where your image is saved.

**Expected:** JSON response with:
- Question text extracted from image
- Step-by-step solution
- Explanation
- Difficulty level

---

### Test 5: List Available Animation Concepts

```bash
curl http://localhost:8000/api/v1/animation/list
```

**Expected:**
```json
{
  "concepts": [
    "quadratic_formula",
    "pythagoras_theorem",
    "linear_equation",
    "area_of_circle"
  ],
  "count": 4
}
```

---

## 🔧 Troubleshooting Common Issues

### Issue 1: "Command not found: python"

**Solution:** Use `python3` instead:

```bash
python3 --version
python3 main.py
```

Or check Python is in PATH:

```bash
where python
# Should show: C:\Users\Lenovo\AppData\Local\Programs\Python\Python312\python.exe
```

---

### Issue 2: "ffmpeg: command not found"

**Solution:** ffmpeg not in PATH. Re-run installation steps or:

```bash
# Windows: Add to PATH manually (see Step 3 above)
# Or use Chocolatey method (easier)
```

Verify:

```bash
where ffmpeg
# Should show: C:\ProgramData\chocolatey\bin\ffmpeg.exe
```

---

### Issue 3: "Port 8000 is already in use"

**Solution:** Something else is using port 8000.

**Option A:** Stop the other program

**Option B:** Change port in `.env`:

```env
PORT=8001
```

Restart server.

---

### Issue 4: "Database connection failed"

**Check:**

1. `.env` has correct Supabase URL and key
2. Supabase project is active (check dashboard)
3. Internet connection is working

**Test connection:**

```bash
python -c "from app.core.database import get_db; db = get_db(); print('Connected!')"
```

---

### Issue 5: "Gemini API key not configured"

**Check `.env` has:**

```env
GEMINI_API_KEY=AIzaSy...
```

**Get a new key if needed:**
https://aistudio.google.com/app/apikey

---

### Issue 6: "ModuleNotFoundError: No module named 'X'"

**Solution:** Virtual environment not activated, or package not installed.

```bash
# Activate venv
source venv/Scripts/activate

# Install missing package
pip install X

# Or reinstall all
pip install -r requirements.txt
```

---

### Issue 7: Manim rendering fails

**Check:**

1. ffmpeg is installed: `ffmpeg -version`
2. LaTeX is installed: `latex --version`
3. Manim is installed: `manim --version`

**Common fix:** Close and reopen terminal after installing ffmpeg/LaTeX.

---

## 🎯 Next Steps

### 1. Customize Animations

Edit `app/services/manim_generator.py` to add more concepts:

- Trigonometric functions
- Circle theorems
- Algebraic identities
- etc.

### 2. Add More Subjects

The Photo Solver already supports all subjects! Test with:
- Physics questions
- Chemistry equations
- Biology diagrams
- History questions
- English grammar

### 3. Deploy to Production

When ready to launch:

1. Change `.env`:
   ```env
   ENV=production
   DEBUG=false
   CORS_ORIGINS=https://yourdomain.com
   ```

2. Set up HTTPS (nginx or Caddy)

3. Add authentication (Supabase Auth or JWT)

4. Deploy to:
   - Railway.app (easiest)
   - AWS/Google Cloud (scalable)
   - DigitalOcean (affordable)

---

## 📞 Getting Help

If you get stuck:

1. Check this guide again
2. Check error message carefully
3. Google the exact error message
4. Check Supabase dashboard for database issues
5. Check Gemini API quota/limits

---

## ✅ Checklist

Before launching:

- [ ] Python 3.10+ installed
- [ ] Git installed
- [ ] ffmpeg installed (`ffmpeg -version` works)
- [ ] LaTeX installed (`latex --version` works)
- [ ] Virtual environment created and activated
- [ ] All packages installed (`pip install -r requirements.txt`)
- [ ] Manim installed (`manim --version` works)
- [ ] `.env` file configured (ENV=development, all API keys present)
- [ ] Database migrations run in Supabase
- [ ] Server starts successfully (`python main.py`)
- [ ] Health check passes (http://localhost:8000/api/v1/health)
- [ ] Git repository initialized (`git init`)
- [ ] First commit created
- [ ] All tests pass

---

**🎉 You're ready to transform Indian education!**

**For more technical details, see:** [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)

**For latest features, see:** [LATEST_UPDATES.md](LATEST_UPDATES.md)
