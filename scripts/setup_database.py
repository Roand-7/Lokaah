"""
Database Setup Script
Runs migrations and populates CBSE Class 10 Math topics

This script will:
1. Check database connection
2. Run migration 002 (scalable curriculum system)
3. Run migration 003 (translation RPC functions)
4. Create CBSE Class 10 Math curriculum entry
5. Populate 60 topics

NOTE: Supabase REST API doesn't support direct SQL execution.
You have 3 options:
  A. Use Supabase SQL Editor (Dashboard) - RECOMMENDED
  B. Use psycopg2 direct PostgreSQL connection
  C. Use Supabase CLI

This script will guide you through Option B (direct PostgreSQL).
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import get_db
from dotenv import load_dotenv

load_dotenv()


def check_connection():
    """Step 1: Verify database connection"""
    print("\n" + "="*70)
    print("STEP 1: Checking Database Connection")
    print("="*70)

    try:
        db = get_db()
        result = db.table('generated_questions').select('id').limit(1).execute()
        print("[OK] Database connection successful")
        return True
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return False


def check_if_migrations_ran():
    """Check if curriculum tables exist"""
    print("\n" + "="*70)
    print("STEP 2: Checking if Migrations Already Ran")
    print("="*70)

    db = get_db()

    # Try to access curriculum tables
    try:
        result = db.table('boards').select('id').limit(1).execute()
        print("[OK] Tables exist - migrations already ran")
        return True
    except Exception as e:
        if 'PGRST205' in str(e):  # Table not found
            print("[INFO] Tables don't exist - need to run migrations")
            return False
        else:
            print(f"[ERROR] Unexpected error: {e}")
            return None


def get_database_url():
    """Get PostgreSQL connection string"""
    supabase_url = os.getenv('SUPABASE_URL')

    if not supabase_url:
        print("[ERROR] SUPABASE_URL not found in .env")
        return None

    # Extract project ref from Supabase URL
    # Format: https://{ref}.supabase.co
    import re
    match = re.search(r'https://([^.]+)\.supabase\.co', supabase_url)

    if not match:
        print(f"[ERROR] Cannot parse Supabase URL: {supabase_url}")
        return None

    project_ref = match.group(1)

    # Construct PostgreSQL connection string
    # You'll need the database password (different from API keys)
    print(f"\nProject Reference: {project_ref}")
    print(f"Host: db.{project_ref}.supabase.co")
    print("\nTo get your database password:")
    print("1. Go to https://supabase.com/dashboard/project/{project_ref}/settings/database")
    print("2. Look for 'Database Settings' > 'Connection String'")
    print("3. Copy the password")

    password = input("\nEnter your database password (or press Enter to skip): ").strip()

    if not password:
        return None

    return f"postgresql://postgres:{password}@db.{project_ref}.supabase.co:5432/postgres"


def run_migrations_with_psycopg2(connection_string):
    """Run migrations using direct PostgreSQL connection"""
    print("\n" + "="*70)
    print("STEP 3: Running Migrations via PostgreSQL")
    print("="*70)

    try:
        import psycopg2
    except ImportError:
        print("[ERROR] psycopg2 not installed")
        print("Install with: pip install psycopg2-binary")
        return False

    migration_files = [
        "supabase/migrations/002_scalable_curriculum_system.sql",
        "supabase/migrations/003_translation_rpc_functions.sql",
    ]

    try:
        conn = psycopg2.connect(connection_string)
        conn.autocommit = True
        cursor = conn.cursor()

        for migration_file in migration_files:
            print(f"\nRunning: {migration_file}")

            with open(migration_file, 'r', encoding='utf-8') as f:
                sql = f.read()

            try:
                cursor.execute(sql)
                print(f"[OK] {migration_file} executed successfully")
            except Exception as e:
                print(f"[ERROR] Failed to execute {migration_file}: {e}")
                return False

        cursor.close()
        conn.close()

        print("\n[OK] All migrations completed successfully")
        return True

    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False


def create_curriculum_via_api():
    """Step 4: Create CBSE Class 10 Math curriculum using Supabase REST API"""
    print("\n" + "="*70)
    print("STEP 4: Creating CBSE Class 10 Math Curriculum")
    print("="*70)

    db = get_db()

    try:
        # Check if CBSE board exists
        board = db.table('boards').select('*').eq('code', 'CBSE').execute()

        if not board.data:
            # Create CBSE board
            board_data = {
                'code': 'CBSE',
                'name': 'CBSE',
                'full_name': 'Central Board of Secondary Education',
                'country': 'India',
                'default_language': 'en',
                'is_active': True
            }
            board = db.table('boards').insert(board_data).execute()
            print("[OK] Created CBSE board")
        else:
            print("[OK] CBSE board already exists")

        board_id = board.data[0]['id']

        # Check if Math subject exists
        subject = db.table('subjects').select('*').eq('code', 'MATH').execute()

        if not subject.data:
            # Create Math subject
            subject_data = {
                'code': 'MATH',
                'name': 'Mathematics',
                'icon': '🧮',
                'color': '#3b82f6',
                'description': 'CBSE Mathematics curriculum',
                'is_active': True
            }
            subject = db.table('subjects').insert(subject_data).execute()
            print("[OK] Created Mathematics subject")
        else:
            print("[OK] Mathematics subject already exists")

        subject_id = subject.data[0]['id']

        # Check if curriculum exists
        curriculum = db.table('curricula').select('*')\
            .eq('board_id', board_id)\
            .eq('subject_id', subject_id)\
            .eq('class_level', 10)\
            .eq('academic_year', '2025-26')\
            .execute()

        if not curriculum.data:
            # Create curriculum
            curriculum_data = {
                'board_id': board_id,
                'subject_id': subject_id,
                'class_level': 10,
                'academic_year': '2025-26',
                'syllabus_version': '1.0',
                'total_marks': 80,
                'passing_marks': 33,
                'time_limit_minutes': 180,
                'ncert_aligned': True,
                'difficulty_avg': 0.5,
                'is_published': True
            }
            curriculum = db.table('curricula').insert(curriculum_data).execute()
            print("[OK] Created CBSE Class 10 Math curriculum")
        else:
            print("[OK] Curriculum already exists")

        curriculum_id = curriculum.data[0]['id']
        print(f"\nCurriculum ID: {curriculum_id}")

        return curriculum_id

    except Exception as e:
        print(f"[ERROR] Failed to create curriculum: {e}")
        return None


def populate_topics(curriculum_id):
    """Step 5: Populate 60 CBSE topics"""
    print("\n" + "="*70)
    print("STEP 5: Populating 60 CBSE Class 10 Math Topics")
    print("="*70)

    # Import and run the populate script
    from populate_cbse_topics import populate_topics as do_populate

    try:
        do_populate(curriculum_id)
        return True
    except Exception as e:
        print(f"[ERROR] Topic population failed: {e}")
        return False


def print_manual_steps():
    """Print manual migration steps if automated fails"""
    print("\n" + "="*70)
    print("MANUAL MIGRATION STEPS (Recommended)")
    print("="*70)

    print("""
If automated migration doesn't work, run migrations manually:

1. Go to Supabase Dashboard: https://supabase.com/dashboard
2. Select your project
3. Go to SQL Editor (left sidebar)
4. Copy and paste the following files one by one:

   File 1: supabase/migrations/002_scalable_curriculum_system.sql
   File 2: supabase/migrations/003_translation_rpc_functions.sql

5. Click "Run" for each file
6. Come back and run: python scripts/setup_database.py --skip-migrations

That's it! The SQL editor is the most reliable method.
""")


def main():
    """Main setup flow"""
    import argparse

    parser = argparse.ArgumentParser(description='Setup LOKAAH database')
    parser.add_argument('--skip-migrations', action='store_true',
                       help='Skip migration step (if already ran manually)')
    parser.add_argument('--manual', action='store_true',
                       help='Show manual migration instructions')

    args = parser.parse_args()

    print("\n" + "="*70)
    print(" LOKAAH DATABASE SETUP")
    print("="*70)

    if args.manual:
        print_manual_steps()
        return

    # Step 1: Check connection
    if not check_connection():
        print("\n[FAILED] Cannot connect to database. Check .env file.")
        return

    # Step 2: Check if migrations needed
    migrations_exist = check_if_migrations_ran()

    if migrations_exist is None:
        print("\n[FAILED] Cannot determine migration status")
        return

    # Step 3: Run migrations (if needed and not skipped)
    if not migrations_exist and not args.skip_migrations:
        print("\n" + "="*70)
        print("Migration Required")
        print("="*70)
        print("""
You have 2 options:

A. Automated (PostgreSQL direct connection)
   - Requires database password
   - Requires psycopg2-binary: pip install psycopg2-binary

B. Manual (Supabase SQL Editor) - RECOMMENDED
   - Go to Supabase Dashboard > SQL Editor
   - Copy/paste migration files
   - Safer and more reliable
        """)

        choice = input("Choose option (A/B) or M for manual steps: ").strip().upper()

        if choice == 'M' or choice == 'B':
            print_manual_steps()
            print("\nOnce you've run the migrations manually, run:")
            print("  python scripts/setup_database.py --skip-migrations")
            return

        elif choice == 'A':
            conn_string = get_database_url()
            if not conn_string:
                print("\n[SKIPPED] Cannot proceed without database password")
                print_manual_steps()
                return

            if not run_migrations_with_psycopg2(conn_string):
                print("\n[FAILED] Migration failed")
                print_manual_steps()
                return

        else:
            print("[CANCELLED] Invalid choice")
            return

    elif migrations_exist:
        print("\n[SKIPPED] Migrations already completed")

    # Step 4: Create curriculum
    curriculum_id = create_curriculum_via_api()

    if not curriculum_id:
        print("\n[FAILED] Cannot create curriculum")
        return

    # Step 5: Populate topics
    if not populate_topics(curriculum_id):
        print("\n[FAILED] Topic population failed")
        return

    print("\n" + "="*70)
    print(" SUCCESS: Database Setup Complete!")
    print("="*70)
    print(f"""
Summary:
  - Migrations: Completed
  - Curriculum: Created (ID: {curriculum_id})
  - Topics: 60 topics populated
  - Status: Ready for production

Next Steps:
  1. Test question generation with curriculum
  2. Run end-to-end tests
  3. Deploy to production
""")


if __name__ == "__main__":
    main()
