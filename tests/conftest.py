"""Ensure project root is on Python path so 'app' can be imported"""
import sys
from pathlib import Path

# Add project root to sys.path so "from app.main import app" works
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
