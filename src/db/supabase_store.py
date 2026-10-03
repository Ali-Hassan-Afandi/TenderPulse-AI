import requests
from datetime import datetime, timezone
from src.config import secret

def configured(): return bool(secret("SUPABASE_URL") and secret("SUPABASE_KEY"))
def _h(prefer=None):
    k=secret("SUPABASE_KEY"); h={"apikey":k,"Authorization":f"Bearer {k}","Content-Type":"application/json"}
    if prefer:h["Prefer"]=prefer
    return h
def _u(table):return f"{secret('SUPABASE_URL').rstrip('/')}/rest/v1/{table}"
def health():
    if not configured():return {"ok":False,"status":"not_configured"}
    try:
        r=requests.get(f"{secret('SUPABASE_URL').rstrip('/')}/rest/v1/",headers=_h(),timeout=10)
        return {"ok":r.ok,"status":"connected" if r.ok else "error","http":r.status_code}
    except Exception as e:return {"ok":False,"status":"error","message":str(e)}
def insert(table,payload):
    if not configured():return {"ok":False,"message":"Supabase not configured"}
    try:
        r=requests.post(_u(table),headers=_h("return=representation"),json=payload,timeout=20)
        return {"ok":r.ok,"status":r.status_code,"message":None if r.ok else r.text[:600]}
    except Exception as e:return {"ok":False,"message":str(e)}
def upsert(table,payload,on_conflict=None):
    if not configured():return {"ok":False,"message":"Supabase not configured"}
    try:
        url=_u(table)+(f"?on_conflict={on_conflict}" if on_conflict else "")
        r=requests.post(url,headers=_h("resolution=merge-duplicates,return=representation"),json=payload,timeout=20)
        return {"ok":r.ok,"status":r.status_code,"message":None if r.ok else r.text[:600]}
    except Exception as e:return {"ok":False,"message":str(e)}
def recent(table,limit=10):
    if not configured():return []
    try:
        r=requests.get(_u(table)+f"?select=*&order=id.desc&limit={limit}",headers=_h(),timeout=15)
        return r.json() if r.ok else []
    except:return []
def count(table):
    if not configured():return 0
    try:
        h=_h();h["Prefer"]="count=exact";r=requests.get(_u(table)+"?select=id&limit=1",headers=h,timeout=15)
        cr=r.headers.get("content-range","0/0");return int(cr.split("/")[-1]) if "/" in cr and cr.split("/")[-1].isdigit() else 0
    except:return 0
def save_company(c):
    return insert("companies",{"company_name":c.get("company_name","Unknown"),"email":c.get("email"),"pec_license":c.get("pec_license"),"profile":c})
def save_tender(t):
    return upsert("tenders",{"id":t.get("id"),"title":t.get("title","Untitled"),"source":t.get("source"),"payload":t,"fingerprint":t.get("fingerprint")},"id")
def save_match(company,tender,score,details):
    return insert("matches",{"company_name":company.get("company_name"),"tender_id":tender.get("id"),"fit_score":score,"details":details})
def save_analysis(tid,name,result):return insert("analyses",{"tender_id":tid,"company_name":name,"result":result})
def save_alert(tid,recipient,status):return insert("alerts",{"tender_id":tid,"recipient":recipient,"status":status})

def list_companies(limit=100):
    return recent("companies",limit)
def list_tenders(limit=500):
    if not configured(): return []
    try:
        r=requests.get(_u("tenders")+f"?select=*&order=id.desc&limit={limit}",headers=_h(),timeout=25)
        return r.json() if r.ok else []
    except:return []
def log_sync(source,status,records,error=None):
    return insert("source_sync_runs",{"source":source,"status":status,"records":records,"error":error})
def tender_exists_fingerprint(fp):
    if not configured():return False
    try:
        r=requests.get(_u("tenders")+f"?select=id&fingerprint=eq.{fp}&limit=1",headers=_h(),timeout=15)
        return r.ok and bool(r.json())
    except:return False
