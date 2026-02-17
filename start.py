#!/usr/bin/env python3
"""
Quick Start Script for LOKAAH
Starts backend server and optionally runs health check
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print('='*60)

def main():
    print_header("🚀 LOKAAH Quick Start")
    
    # Check .env file
    if not Path('.env').exists():
        print("❌ Error: .env file not found!")
        print("   Please copy .env.example to .env and fill in your API keys")
        return 1
    
    print("✅ Environment file found")
    
    # Check virtual environment
    venv_python = Path('.venv/Scripts/python.exe')
    if not venv_python.exists():
        print("❌ Error: Virtual environment not found!")
        print("   Run: python -m venv .venv")
        print("   Then: pip install -r requirements.txt")
        return 1
    
    print("✅ Virtual environment found")
    print("\n📡 Starting Backend Server...")
    print("   Server will run on http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print("\n   Press Ctrl+C to stop\n")
    
    try:
        # Start the server
        subprocess.run([str(venv_python), 'main.py'])
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        return 0

if __name__ == '__main__':
    sys.exit(main())
