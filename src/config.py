import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

def secret(name, default=None):
    """Read from environment first (workers), then Streamlit secrets (app)."""
    value = os.environ.get(name)
    if value not in (None, ""):
        return value
    try:
        import streamlit as st
        return st.secrets.get(name, default)
    except Exception:
        return default

GROQ_MODEL = secret("GROQ_MODEL", "llama-3.3-70b-versatile")
