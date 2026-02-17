# 🗄️ Database Migration Guide

## Quick Instructions (5 minutes)

### Step 1: Access Supabase Dashboard
1. Open browser: https://supabase.com/dashboard
2. Click on your project
3. Click **"SQL Editor"** in the left sidebar

---

### Step 2: Run Migration 1 - Agentic Memory System

#### What it does:
Creates 6 tables for AI agent memory and student tracking:
- Conversation history storage
- Session summaries (auto-generated every 10 turns)
- Bayesian Knowledge Tracing for concept mastery
- Detailed attempt history
- Learning session metrics
- Student answers to questions

#### How to run:
1. In Supabase SQL Editor, click **"New query"**
2. Open file: `supabase/migrations/002_agentic_memory.sql`
3. **Copy ALL content** (Ctrl+A, Ctrl+C)
4. **Paste** into Supabase SQL Editor
5. Click **"Run"** button (bottom right)
6. Wait for success message: ✅ "Success. No rows returned"
7. You should see in logs: "✅ Agentic Memory System migration completed successfully!"

#### Verify:
- Click "Table Editor" in left sidebar
- You should see these NEW tables:
  - conversation_history
  - session_summaries
  - concept_mastery
  - concept_attempts
  - learning_sessions
  - student_attempts

---

### Step 3: Run Migration 2 - Photo Solver

#### What it does:
Creates 1 table for storing solved questions from photo uploads:
- Photo question storage with image hash deduplication
- Subject-specific organization
- Confidence scores and difficulty tracking

#### How to run:
1. In Supabase SQL Editor, click **"New query"** again
2. Open file: `supabase/migrations/003_photo_solver.sql`
3. **Copy ALL content** (Ctrl+A, Ctrl+C)
4. **Paste** into Supabase SQL Editor
5. Click **"Run"** button
6. Wait for success message

#### Verify:
- Click "Table Editor" in left sidebar
- You should see this NEW table:
  - solved_questions

---

### Step 4: Verify All Tables

After running both migrations, your database should have these tables:

✅ **From Agentic Memory (002):**
1. conversation_history
2. session_summaries
3. concept_mastery
4. concept_attempts
5. learning_sessions
6. student_attempts

✅ **From Photo Solver (003):**
7. solved_questions

✅ **From Curriculum System (002_scalable):**
8. boards
9. subjects
10. curricula
11. chapters
12. sections
13. subsections
14. learning_outcomes
And many more...

---

## Troubleshooting

### Error: "relation already exists"
**Solution:** Table was already created. This is OK, you can skip that migration.

### Error: "syntax error near..."
**Solution:** Make sure you copied the ENTIRE file content. Try again.

### Error: "database connection failed"
**Solution:** 
1. Check your Supabase project is not paused
2. Refresh the Supabase dashboard
3. Try again

### Success but no tables visible
**Solution:**
1. Click "Table Editor" tab
2. Click refresh icon
3. If still not visible, check "SQL Editor" → "History" for any errors

---

## After Migration Success

### Test the database connection:
```powershell
# In your PowerShell terminal
curl http://localhost:8000/api/v1/health -UseBasicParsing
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",  ← Should say "connected"
  "oracle_engine": "ready"
}
```

### Test storing a conversation:
```powershell
curl -X POST http://localhost:8000/api/v1/veda/chat `
  -H "Content-Type: application/json" `
  -d '{\"message\":\"Hello VEDA\",\"session_id\":\"test123\"}' `
  -UseBasicParsing
```

Then check in Supabase:
1. Go to "Table Editor"
2. Click "conversation_history" table
3. You should see your message stored!

---

## Migration File Locations

Both files are in your project:

```
C:\Users\Lenovo\lokaah_app\supabase\migrations\
├── 002_agentic_memory.sql              ← Run this first
├── 002_scalable_curriculum_system.sql  ← Already run (if you have boards/subjects tables)
└── 003_photo_solver.sql                ← Run this second
```

---

## Quick Copy Commands

If you're in VSCode:

1. **Open file:** Ctrl+P → type filename → Enter
2. **Select all:** Ctrl+A
3. **Copy:** Ctrl+C
4. **Paste in Supabase:** Ctrl+V
5. **Run:** Click "Run" button or Ctrl+Enter

---

## ✅ Completion Verification

After running both migrations, you should have:

| Feature | Table | Status |
|---------|-------|--------|
| Chat memory | conversation_history | ✅ |
| Session tracking | session_summaries | ✅ |
| Concept mastery | concept_mastery | ✅ |
| Attempt history | concept_attempts | ✅ |
| Learning metrics | learning_sessions | ✅ |
| Student answers | student_attempts | ✅ |
| Photo solver | solved_questions | ✅ |

---

**Estimated time:** 5 minutes  
**Difficulty:** Easy (just copy-paste)  
**Required:** Yes (for VEDA memory and tracking features)

Once complete, your LOKAAH platform will be 100% operational! 🚀
