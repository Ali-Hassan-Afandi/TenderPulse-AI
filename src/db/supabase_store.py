import requests
from src.config import secret

def configured():
    return bool(secret("SUPABASE_URL") and secret("SUPABASE_KEY"))

def _headers():
    key=secret("SUPABASE_KEY")
    return {"apikey":key,"Authorization":f"Bearer {key}","Content-Type":"application/json","Prefer":"return=representation"}

def health():
    if not configured():
        return {"status":"optional","database":"session-state","message":"Add Supabase secrets for persistence."}
    try:
        r=requests.get(f"{secret('SUPABASE_URL').rstrip('/')}/rest/v1/",headers=_headers(),timeout=10)
        return {"status":"connected" if r.ok else "error","database":"supabase","http":r.status_code}
    except Exception as e:
        return {"status":"error","database":"supabase","message":str(e)}

def insert(table,payload):
    if not configured(): return {"ok":False,"message":"Supabase not configured."}
    r=requests.post(f"{secret('SUPABASE_URL').rstrip('/')}/rest/v1/{table}",headers=_headers(),json=payload,timeout=15)
    return {"ok":r.ok,"status":r.status_code}
