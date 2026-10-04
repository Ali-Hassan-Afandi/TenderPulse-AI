import json, requests
from src.config import secret

def configured():
    return bool(secret("SUPABASE_URL")) and bool(secret("SUPABASE_KEY"))

def _base():
    return str(secret("SUPABASE_URL","")).rstrip("/") + "/rest/v1/"

def _url(table):
    return _base()+table

def _headers(prefer=None):
    key=secret("SUPABASE_KEY","")
    h={"apikey":key,"Authorization":f"Bearer {key}","Content-Type":"application/json"}
    if prefer:h["Prefer"]=prefer
    return h

# Legacy compatibility alias
def _h(prefer=None): return _headers(prefer)

def health():
    if not configured(): return {"ok":False,"status":"not configured"}
    try:
        r=requests.get(_url("companies")+"?select=*&limit=1",headers=_headers(),timeout=15)
        return {"ok":r.ok,"status":"connected" if r.ok else f"HTTP {r.status_code}"}
    except Exception as e:return {"ok":False,"status":str(e)}

def insert(table,payload):
    if not configured():return {"ok":False,"error":"Supabase not configured"}
    try:
        r=requests.post(_url(table),headers=_headers("return=representation"),json=payload,timeout=20)
        return {"ok":r.ok,"data":r.json() if r.text else [],"status":r.status_code,"error":None if r.ok else r.text[:800]}
    except Exception as e:return {"ok":False,"error":str(e)}

def upsert(table,payload,on_conflict=None):
    if not configured():return {"ok":False,"error":"Supabase not configured"}
    url=_url(table)
    if on_conflict:url+=f"?on_conflict={on_conflict}"
    try:
        r=requests.post(url,headers=_headers("resolution=merge-duplicates,return=representation"),json=payload,timeout=20)
        return {"ok":r.ok,"data":r.json() if r.text else [],"status":r.status_code,"error":None if r.ok else r.text[:800]}
    except Exception as e:return {"ok":False,"error":str(e)}

def recent(table,limit=50):
    if not configured():return []
    for order in ("id.desc","created_at.desc"):
        try:
            r=requests.get(_url(table)+f"?select=*&order={order}&limit={int(limit)}",headers=_headers(),timeout=20)
            if r.ok:return r.json()
        except:pass
    return []

def count(table):
    if not configured():return 0
    try:
        h=_headers();h["Prefer"]="count=exact"
        r=requests.get(_url(table)+"?select=id&limit=1",headers=h,timeout=15)
        cr=r.headers.get("content-range","")
        return int(cr.split("/")[-1]) if "/" in cr and cr.split("/")[-1].isdigit() else 0
    except:return 0

def _company_payload(profile):
    # Keep compatibility with the existing V7 Supabase schema: company data lives in profile JSON.
    return {"company_name":profile.get("company_name",""),"email":profile.get("email",""),"profile":profile}

def save_company(profile):
    return insert("companies",_company_payload(profile))

def save_or_update_company(profile):
    """Update a saved company when identifiable; otherwise insert it. Never makes persistence depend on Streamlit session."""
    if not configured():return {"ok":False,"error":"Supabase not configured"}
    name=profile.get("company_name","").strip()
    lic=profile.get("pec_license","").strip()
    try:
        rows=recent("companies",250)
        target=None
        for row in rows:
            p=row.get("profile") if isinstance(row.get("profile"),dict) else {}
            if lic and p.get("pec_license")==lic:target=row;break
            if name and (p.get("company_name")==name or row.get("company_name")==name):target=row;break
        if target and target.get("id") is not None:
            r=requests.patch(_url("companies")+f"?id=eq.{target['id']}",headers=_headers("return=representation"),json=_company_payload(profile),timeout=20)
            return {"ok":r.ok,"data":r.json() if r.text else [],"status":r.status_code,"error":None if r.ok else r.text[:800]}
    except Exception:
        pass
    return save_company(profile)

def saved_companies(limit=250):
    return selectable_companies(limit)

def selectable_companies(limit=250):
    out=[];seen=set()
    for row in recent("companies",limit):
        p=row.get("profile") if isinstance(row.get("profile"),dict) else dict(row)
        for k in ("company_name","email","pec_license"):
            if not p.get(k) and row.get(k):p[k]=row.get(k)
        key=p.get("pec_license") or p.get("company_name")
        if key and key not in seen:
            seen.add(key);out.append(p)
    return out

def save_tender(t):
    payload={"id":str(t.get("id","")),"title":t.get("title",""),"source":t.get("source",""),
             "payload":t,"fingerprint":t.get("fingerprint")}
    return upsert("tenders",payload,"id")

def list_tenders(limit=500):
    if not configured():return []
    try:
        r=requests.get(_url("tenders")+f"?select=*&order=id.desc&limit={int(limit)}",headers=_headers(),timeout=25)
        return r.json() if r.ok else []
    except:return []

def save_match(tender_id,company_name,score,payload=None):
    return insert("matches",{"tender_id":str(tender_id),"company_name":company_name,"score":score,"payload":payload or {}})

def company_matches(company_name,limit=100):
    if not configured():return []
    try:
        from urllib.parse import quote
        r=requests.get(_url("matches")+f"?select=*&company_name=eq.{quote(str(company_name),safe='')}&order=id.desc&limit={int(limit)}",headers=_headers(),timeout=20)
        return r.json() if r.ok else []
    except:return []

def save_analysis(tender_id,company_name,payload):
    return insert("analyses",{"tender_id":str(tender_id),"company_name":company_name,"payload":payload})

def save_alert(tender_id,company_name,recipient,status="sent",payload=None):
    return insert("alerts",{"tender_id":str(tender_id),"company_name":company_name,"recipient":recipient,"status":status,"payload":payload or {}})

def log_sync(source,status,records,error=None):
    return insert("source_sync_runs",{"source":source,"status":status,"records":records,"error":error})

def tender_exists_fingerprint(fp):
    if not configured() or not fp:return False
    try:
        r=requests.get(_url("tenders")+f"?select=id&fingerprint=eq.{fp}&limit=1",headers=_headers(),timeout=15)
        return r.ok and bool(r.json())
    except:return False

def list_companies(limit=100):
    return selectable_companies(limit)
