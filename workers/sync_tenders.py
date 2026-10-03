import os,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.connectors.registry import fetch_all
from src.db.supabase_store import save_tender,log_sync,tender_exists_fingerprint
def main():
    rows,health=fetch_all()
    saved=0
    for t in rows:
        if not tender_exists_fingerprint(t.get("fingerprint","")):
            r=save_tender(t);saved+=1 if r.get("ok") else 0
    for source,h in health.items():log_sync(source,"ok" if h["ok"] else "error",h["records"],h.get("error"))
    print(json.dumps({"fetched":len(rows),"saved":saved,"health":health},indent=2))
if __name__=="__main__":main()
