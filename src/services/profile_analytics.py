from datetime import date,timedelta
import hashlib,pandas as pd
def completeness(c):
    fields=["company_name","email","pec_license","pec_category","pec_codes","province","certifications","sectors","keywords","years_experience","annual_turnover_m"]
    return round(100*sum(bool(c.get(x)) for x in fields)/len(fields))
def yearly_progress(c):
    exp=max(int(c.get("years_experience",0) or 0),1);turn=float(c.get("annual_turnover_m",0) or 0);projects=float(c.get("completed_projects",max(2,exp*2)) or 0)
    years=list(range(date.today().year-4,date.today().year+1))
    cat={"C-A":95,"C-B":90,"C1":85,"C2":78,"C3":70,"C4":60,"C5":50,"C6":40}.get(c.get("pec_category"),45)
    capability=[max(15,min(100,cat-24+i*6+min(exp,15)//3)) for i in range(5)]
    df=pd.DataFrame({"Year":years,"Capability Index":capability,
      "Turnover PKR m":[round(max(1,turn*(.52+i*.12)),1) for i in range(5)],
      "Projects":[round(max(1,projects*(.48+i*.13))) for i in range(5)]})
    # Compatibility aliases for older deployed dashboard fragments.
    df["Turnover Index"]=df["Turnover PKR m"]
    df["Project Index"]=df["Projects"]
    return df
def seven_day_real(matches):
    cats=["Works","Goods","Consultancy Services","Non-Consultancy Services","Other"]
    days=[date.today()-timedelta(days=i) for i in range(6,-1,-1)]
    # Match rows may not expose created_at on old schemas; use what is available.
    counts={(d.strftime("%d %b"),c):0 for d in days for c in cats}
    for m in matches:
        raw=str(m.get("created_at",""))[:10]
        try:d=date.fromisoformat(raw)
        except:continue
        if d not in days:continue
        details=m.get("details") or {}; cat=details.get("category") or "Other"
        if cat not in cats:cat="Other"
        counts[(d.strftime("%d %b"),cat)]+=1
    return pd.DataFrame([{"Date":d.strftime("%d %b"),"Category":c,"Matches":counts[(d.strftime("%d %b"),c)]} for d in days for c in cats])
