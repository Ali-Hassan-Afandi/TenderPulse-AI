from datetime import date,timedelta
import pandas as pd
def completeness(c):
    fields=["company_name","email","pec_license","pec_category","pec_codes","province","certifications","sectors","keywords","years_experience","annual_turnover_m"]
    present=sum(bool(c.get(x)) for x in fields)
    return round(100*present/len(fields))
def yearly_progress(c):
    exp=max(int(c.get("years_experience",0)),1);turn=float(c.get("annual_turnover_m",0) or 0);projects=float(c.get("completed_projects",max(4,exp*2)) or 0)
    years=list(range(date.today().year-4,date.today().year+1))
    return pd.DataFrame({"Year":years,"Capability Index":[max(20,48+i*9) for i in range(5)],"Turnover Index":[round(max(5,turn*(.55+i*.1125)),1) for i in range(5)],"Project Index":[round(max(2,projects*(.5+i*.125)),1) for i in range(5)]})
def seven_day_matches():
    cats=["Works","Goods","Consultancy Services","Non-Consultancy Services"]
    rows=[]
    today=date.today()
    for i in range(6,-1,-1):
        d=today-timedelta(days=i)
        for j,c in enumerate(cats):
            rows.append({"Date":d.strftime("%d %b"),"Category":c,"Matches":max(0,((7-i)*3+j*2)%11 + (3 if c=="Works" else 1))})
    return pd.DataFrame(rows)
