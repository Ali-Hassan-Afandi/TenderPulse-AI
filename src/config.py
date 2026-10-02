from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

def secret(name, default=None):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default

APP_NAME = "TenderPulse AI"
GROQ_MODEL = secret("GROQ_MODEL", "llama-3.3-70b-versatile")
