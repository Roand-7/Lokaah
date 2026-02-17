from supabase import create_client, Client
from app.core.config import settings

# Service role client (bypasses RLS - for backend use only)
try:
    supabase: Client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_KEY,
    )
except Exception as exc:
    print(f"Supabase connection warning: {exc}")
    print("Retrying with SSL verification disabled (dev mode only)")
    import httpx

    supabase: Client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_KEY,
        options={
            "httpx_client": httpx.Client(verify=False, http2=True),
        },
    )


def get_db():
    """Dependency for database operations"""
    return supabase


async def get_user_profile(user_id: str):
    """Fetch user profile with error handling"""
    try:
        response = supabase.table('profiles').select('*').eq('id', user_id).single().execute()
        return response.data
    except Exception as exc:
        print(f"Error fetching profile: {exc}")
        return None


async def create_learning_session(user_id: str, chapter: str, concept: str = None):
    """Create new learning session"""
    data = {
        'user_id': user_id,
        'chapter': chapter,
        'concept': concept,
        'status': 'active',
    }
    try:
        response = supabase.table('learning_sessions').insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as exc:
        print(f"Error creating session: {exc}")
        return None


async def save_question(session_id: str, user_id: str, question_data: dict):
    """Save generated question to database"""
    db_data = {
        'session_id': session_id,
        'user_id': user_id,
        'question_text': question_data['text'],
        'concept': question_data['concept'],
        'chapter': question_data['chapter'],
        'difficulty': question_data['difficulty'],
        'source': question_data['source'],
        'jsxgraph_code': question_data.get('jsxgraph_code'),
        'correct_answer': question_data['correct_answer'],
        'hints': question_data.get('hints', []),
        'solution_steps': question_data.get('solution_steps', []),
    }
    try:
        response = supabase.table('generated_questions').insert(db_data).execute()
        return response.data[0] if response.data else None
    except Exception as exc:
        print(f"Error saving question: {exc}")
        return None


async def record_attempt(question_id: str, user_id: str, session_id: str, attempt_data: dict):
    """Record student attempt"""
    data = {
        'question_id': question_id,
        'user_id': user_id,
        'session_id': session_id,
        'answer_data': attempt_data['answer'],
        'is_correct': attempt_data['is_correct'],
        'confidence_score': attempt_data.get('confidence'),
        'time_taken_seconds': attempt_data.get('time_taken'),
        'hints_used': attempt_data.get('hints_used', 0),
    }
    try:
        response = supabase.table('student_attempts').insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as exc:
        print(f"Error recording attempt: {exc}")
        return None


async def log_veda_interaction(user_id: str, session_id: str, interaction: dict):
    """Log VEDA teaching interaction"""
    data = {
        'user_id': user_id,
        'session_id': session_id,
        'question_id': interaction.get('question_id'),
        'interaction_type': interaction['type'],
        'message': interaction['message'],
        'context': interaction.get('context', {}),
    }
    try:
        response = supabase.table('veda_interactions').insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as exc:
        print(f"Error logging interaction: {exc}")
        return None
