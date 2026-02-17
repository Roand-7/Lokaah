"""
Run Supabase Migrations Locally
Applies all SQL migrations to the database
"""

import os
from pathlib import Path
from app.database import get_db

def run_migrations():
    """Execute all migration files in order"""
    migrations_dir = Path("supabase/migrations")

    if not migrations_dir.exists():
        print(f"[ERROR] Migrations directory not found: {migrations_dir}")
        return

    # Get all .sql files sorted by name
    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        print("[WARN] No migration files found")
        return

    print("\n" + "="*60)
    print("DATABASE MIGRATIONS")
    print("="*60)
    print(f"Found {len(migration_files)} migration files\n")

    db = get_db()

    for migration_file in migration_files:
        print(f"[RUN] {migration_file.name}...")

        try:
            # Read SQL
            with open(migration_file, 'r', encoding='utf-8') as f:
                sql = f.read()

            # Execute (Supabase client doesn't directly support raw SQL)
            # For local development, we need to use psycopg2 or run via CLI
            print(f"  [INFO] Migration file ready: {migration_file.name}")
            print(f"  [INFO] Please run this via Supabase CLI or pgAdmin")
            print(f"  [INFO] Command: supabase db push")

        except Exception as e:
            print(f"  [ERROR] {e}")

    print("\n" + "="*60)
    print("MIGRATION INSTRUCTIONS")
    print("="*60)
    print("\nTo apply migrations, use one of these methods:")
    print("\n1. Supabase CLI (Recommended):")
    print("   supabase db reset")
    print("   OR")
    print("   supabase db push")
    print("\n2. Supabase Dashboard:")
    print("   - Go to SQL Editor")
    print("   - Copy-paste migration SQL")
    print("   - Execute")
    print("\n3. Direct PostgreSQL:")
    print("   psql -U postgres -d your_db -f supabase/migrations/002_scalable_curriculum_system.sql")
    print("\n" + "="*60)


if __name__ == "__main__":
    run_migrations()
