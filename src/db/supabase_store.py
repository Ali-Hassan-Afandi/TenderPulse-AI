import requests
from src.config import secret

def configured():
    return bool(secret("SUPABASE_URL") and secret("SUPABASE_KEY"))

def _headers(prefer=None):
    key = secret("SUPABASE_KEY")
    headers = {
        "apikey": key or "",
        "Authorization": f"Bearer {key or ''}",
        "Content-Type": "application/json",
    }
    if prefer:
        headers["Prefer"] = prefer
    return headers

def _url(table):
    base = (secret("SUPABASE_URL") or "").rstrip("/")
    return f"{base}/rest/v1/{table}"

def health():
    if not configured():
        return {"ok": False, "status": "not_configured", "database": "supabase"}
    try:
        # Test a real application table instead of only the REST root.
        r = requests.get(
            _url("companies") + "?select=id&limit=1",
            headers=_headers(),
            timeout=15,
        )
        return {
            "ok": r.ok,
            "status": "connected" if r.ok else "error",
            "database": "supabase",
            "http": r.status_code,
            "message": None if r.ok else r.text[:400],
        }
    except Exception as exc:
        return {"ok": False, "status": "error", "database": "supabase", "message": str(exc)}

def insert(table, payload):
    if not configured():
        return {"ok": False, "message": "Supabase not configured."}
    try:
        r = requests.post(
            _url(table),
            headers=_headers("return=representation"),
            json=payload,
            timeout=20,
        )
        return {
            "ok": r.ok,
            "status": r.status_code,
            "data": r.json() if r.ok and r.text else None,
            "message": None if r.ok else r.text[:600],
        }
    except Exception as exc:
        return {"ok": False, "message": str(exc)}

def upsert(table, payload, on_conflict=None):
    if not configured():
        return {"ok": False, "message": "Supabase not configured."}
    try:
        url = _url(table)
        if on_conflict:
            url += f"?on_conflict={on_conflict}"
        r = requests.post(
            url,
            headers=_headers("resolution=merge-duplicates,return=representation"),
            json=payload,
            timeout=20,
        )
        return {
            "ok": r.ok,
            "status": r.status_code,
            "data": r.json() if r.ok and r.text else None,
            "message": None if r.ok else r.text[:600],
        }
    except Exception as exc:
        return {"ok": False, "message": str(exc)}

def recent(table, limit=10):
    if not configured():
        return []
    try:
        r = requests.get(
            _url(table) + f"?select=*&order=id.desc&limit={int(limit)}",
            headers=_headers(),
            timeout=20,
        )
        return r.json() if r.ok else []
    except Exception:
        return []

def count(table):
    if not configured():
        return 0
    try:
        headers = _headers()
        headers["Prefer"] = "count=exact"
        r = requests.get(
            _url(table) + "?select=id&limit=1",
            headers=headers,
            timeout=15,
        )
        total = r.headers.get("content-range", "0/0").split("/")[-1]
        return int(total) if total.isdigit() else 0
    except Exception:
        return 0

def save_company(company):
    return insert(
        "companies",
        {
            "company_name": company.get("company_name", "Unknown"),
            "email": company.get("email"),
            "pec_license": company.get("pec_license"),
            "profile": company,
        },
    )

def save_tender(tender):
    payload = {
        "id": tender.get("id"),
        "title": tender.get("title", "Untitled"),
        "source": tender.get("source"),
        "payload": tender,
        "fingerprint": tender.get("fingerprint"),
    }
    return upsert("tenders", payload, "id")

def save_match(company, tender, score, details):
    return insert(
        "matches",
        {
            "company_name": company.get("company_name"),
            "tender_id": tender.get("id"),
            "fit_score": score,
            "details": details,
        },
    )

def save_analysis(tender_id, company_name, result):
    return insert(
        "analyses",
        {"tender_id": tender_id, "company_name": company_name, "result": result},
    )

def save_alert(tender_id, recipient, status):
    return insert(
        "alerts",
        {"tender_id": tender_id, "recipient": recipient, "status": status},
    )

def list_companies(limit=100):
    return recent("companies", limit)

def list_tenders(limit=500):
    if not configured():
        return []
    try:
        r = requests.get(
            _url("tenders") + f"?select=*&order=id.desc&limit={int(limit)}",
            headers=_headers(),
            timeout=25,
        )
        return r.json() if r.ok else []
    except Exception:
        return []

def log_sync(source, status, records, error=None):
    return insert(
        "source_sync_runs",
        {
            "source": source,
            "status": status,
            "records": int(records or 0),
            "error": error,
        },
    )

def tender_exists_fingerprint(fingerprint):
    if not configured() or not fingerprint:
        return False
    try:
        r = requests.get(
            _url("tenders") + "?select=id&fingerprint=eq." + fingerprint + "&limit=1",
            headers=_headers(),
            timeout=15,
        )
        return r.ok and bool(r.json())
    except Exception:
        return False
