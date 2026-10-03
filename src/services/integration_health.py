from src.db.supabase_store import health as supabase_health
from src.services.email_service import configured as smtp_configured
from src.services.groq_service import available as groq_available

def run_health():
    g=bool(groq_available()); m=bool(smtp_configured()); d=supabase_health()
    return {"groq":{"ok":g,"status":"configured" if g else "missing"},
            "supabase":d,
            "smtp":{"ok":m,"status":"configured" if m else "missing"}}
