"""
List available Gemini models
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

from google import genai

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("No GEMINI_API_KEY found")
    exit(1)

print(f"API Key: {api_key[:20]}...")
print("\nConnecting to Gemini...")

try:
    client = genai.Client(api_key=api_key)
    
    print("\nAvailable models:")
    print("=" * 60)
    
    models = client.models.list()
    for model in models:
        print(f"✅ {model.name}")
        if hasattr(model, 'display_name'):
            print(f"   Display: {model.display_name}")
        if hasattr(model, 'description'):
            print(f"   Description: {model.description[:80] if len(model.description) > 80 else model.description}")
        print()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
