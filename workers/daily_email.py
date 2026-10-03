import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.db.supabase_store import list_companies,list_tenders,save_match,save_alert
from src.services.matcher import top_matches
from src.services.email_service import send_alert
def main():
    companies=list_companies(100); tenders=list_tenders(500)
    for row in companies:
        c=row.get("profile") or row
        email=c.get("email")
        if not email:continue
        normalized=[x.get("payload") or x for x in tenders]
        matches=top_matches(c,normalized,45,10)
        if not matches:continue
        lines=["TenderPulse AI — Morning Tender Radar","",f"Company: {c.get('company_name')}",""]
        for i,t in enumerate(matches,1):
            lines += [f"{i}. {t.get('title')}","Fit: "+str(t.get("match",{}).get("fit"))+"%",f"Category: {t.get('category')}",f"Deadline: {t.get('deadline')}",f"Official: {t.get('source_url')}",""]
            save_match(c,t,t["match"]["fit"],t["match"])
        ok,msg=send_alert(email,"TenderPulse AI | Daily matched tenders","\n".join(lines))
        save_alert("DAILY",email,"sent" if ok else "failed")
        print(email,ok,msg)
if __name__=="__main__":main()
