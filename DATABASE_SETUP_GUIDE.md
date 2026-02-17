# Database Setup Guide - CBSE Class 10 Math Foundation

## 🎯 Goal
Set up the complete database schema for CBSE Class 10 Math with multi-board scalability.

---

## 📋 Prerequisites

- Supabase project created
- Supabase CLI installed (or access to Supabase Dashboard)
- Database connection string in `.env`

---

## 🚀 Setup Steps

### Method 1: Supabase CLI (Recommended)

```bash
# 1. Initialize Supabase (if not done)
supabase init

# 2. Link to your project
supabase link --project-ref YOUR_PROJECT_REF

# 3. Apply migrations
supabase db push

# 4. Verify migrations
supabase db diff
```

### Method 2: Supabase Dashboard

1. Go to your Supabase Dashboard
2. Navigate to **SQL Editor**
3. Copy and run migrations in order:

**Step 1: Run `002_scalable_curriculum_system.sql`**
- This creates all 15+ tables
- Creates RLS policies
- Creates indexes
- Seeds CBSE Class 10 Math curriculum

**Step 2: Run `003_translation_rpc_functions.sql`**
- Creates translation helper functions
- Creates indexes for translation lookups

---

## 📊 What Gets Created

### Tables (15+):

#### Core Curriculum Tables:
- `boards` - Educational boards (CBSE, Karnataka, Kerala, etc.)
- `subjects` - Academic subjects (Math, Science, etc.)
- `curricula` - Board + Subject + Class combinations
- `topics` - Hierarchical chapter structure (60 topics for CBSE Math)
- `question_patterns` - JSON-based pattern templates

#### Translation & i18n:
- `translations` - Multi-language content cache

#### Student Progress:
- `student_curriculum_progress` - Overall progress per curriculum
- `topic_mastery` - Mastery scores per topic
- `concept_mastery` - Fine-grained concept tracking
- `concept_attempts` - Individual attempt history

#### Gamification:
- `student_gamification` - XP, level, streaks, total_study_time
- `achievements` - Achievement definitions (badges)
- `user_achievements` - User's earned achievements
- `leaderboard_entries` - Leaderboard rankings

#### Assessments:
- `mock_tests` - Mock exam configurations
- `mock_test_attempts` - Student attempt records

---

## 🔍 Verify Installation

After running migrations, verify with these queries:

```sql
-- Check tables were created
SELECT tablename FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- Check CBSE curriculum was seeded
SELECT * FROM boards WHERE code = 'CBSE';
SELECT * FROM subjects WHERE code = 'MATH';
SELECT * FROM curricula WHERE class_level = 10;

-- Check RLS policies
SELECT tablename, policyname FROM pg_policies;
```

Expected output:
- 15+ tables created
- 1 board (CBSE)
- 1 subject (Math)
- 1 curriculum (CBSE Class 10 Math 2024-25)
- RLS policies on all student tables

---

## 📝 Populate Topics (After Migrations)

Once migrations are complete, populate the 60 CBSE Class 10 Math topics:

```bash
# Get the curriculum ID from database
# Then run:
python scripts/populate_cbse_topics.py <curriculum_id>
```

OR manually get curriculum ID and update the script:

```python
# In populate_cbse_topics.py, replace placeholder with actual UUID
curriculum_id = "actual-uuid-from-database"
```

---

## 🧪 Test the Setup

After migrations and topic population:

```python
# Test CurriculumManager
from app.curriculum import get_curriculum_manager
from app.database import get_db

cm = get_curriculum_manager(get_db())

# Should return CBSE Class 10 Math curriculum
curriculum = await cm.get_curriculum(
    board="CBSE",
    subject="MATH",
    class_level=10,
    academic_year="2024-25"
)

# Should return 60 topics
topics = await cm.get_topics(curriculum.id)
print(f"Topics loaded: {len(topics)}")  # Should be 60

# Should return topic hierarchy
hierarchy = await cm.get_topic_hierarchy(curriculum.id)
print(f"Chapters: {len(hierarchy['chapters'])}")  # Should be 15
```

---

## 🔧 Troubleshooting

### Issue: "relation does not exist"
**Solution:** Migrations not run. Follow Method 1 or 2 above.

### Issue: "curriculum not found"
**Solution:** Check if seed data was inserted:
```sql
SELECT * FROM curricula;
```
If empty, re-run migration `002_scalable_curriculum_system.sql`

### Issue: "topics table empty"
**Solution:** Run `populate_cbse_topics.py` script after getting curriculum ID:
```sql
SELECT id FROM curricula WHERE class_level = 10;
```

### Issue: RLS policy errors
**Solution:** Ensure you're connected as the correct user. RLS policies allow:
- Public read access to boards, subjects, curricula, topics
- Authenticated user access to student progress tables

---

## ✅ Success Checklist

- [ ] Migrations run successfully
- [ ] 15+ tables exist in database
- [ ] CBSE board seeded
- [ ] Math subject seeded
- [ ] CBSE Class 10 Math curriculum seeded
- [ ] RLS policies active
- [ ] Indexes created
- [ ] 60 topics populated
- [ ] CurriculumManager can fetch curriculum
- [ ] Topics load correctly

---

## 📚 Next Steps

After database setup is complete:

1. **Test Pattern Generation**
   ```python
   from app.oracle.pattern_manager import PatternManager
   pm = PatternManager("app/oracle/patterns")
   question = pm.generate_question("quadratic_nature_of_roots")
   ```

2. **Test Translation Service**
   ```python
   from app.services.translation_service import get_translation_service
   ts = get_translation_service(gemini_client, db)
   hindi = await ts.translate("Solve the equation", "hi")
   ```

3. **Wire into ORACLE Agent**
   - Integrate PatternManager into ORACLE's question generation
   - Test full VEDA → ORACLE → Question flow

4. **Run End-to-End Tests**
   - Start FastAPI backend
   - Generate practice questions via API
   - Verify zero-hallucination math

---

## 🎯 Foundation Complete When:

✅ All migrations applied
✅ 60 topics in database
✅ CurriculumManager working
✅ PatternManager generating questions
✅ TranslationService translating
✅ Zero-hallucination math verified

**Then proceed to Phase 4: LLM-ify Agents** 🚀
