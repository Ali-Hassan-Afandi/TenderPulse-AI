from pathlib import Path
import os
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

def secret(name, default=None):
    value=os.environ.get(name)
    if value is not None and value!="": return value
    try:
        import streamlit as st
        return st.secrets.get(name,default)
    except Exception:
        return default
