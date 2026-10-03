import re
CATEGORY_RANK={"C-A":7,"C-B":6,"C1":5,"C2":4,"C3":3,"C4":2,"C5":1,"C6":0}
def _tokens(x):return set(re.findall(r"[a-z0-9]+"," ".join(x if isinstance(x,list) else [str(x)]).lower()))
def fit(company,tender):
    text=" ".join(str(tender.get(k,"")) for k in ["title","description","category","agency"]).lower()
    words=_tokens(company.get("keywords",[])+company.get("sectors",[])+company.get("pec_codes",[]))
    overlap=[w for w in words if len(w)>2 and w in text]
    keyword=min(35,len(overlap)*7)
    reqcat=tender.get("min_category");cat=25 if not reqcat else (25 if CATEGORY_RANK.get(company.get("pec_category"),-1)>=CATEGORY_RANK.get(reqcat,99) else 0)
    req=set(tender.get("required_codes") or []); cc=set(company.get("pec_codes") or [])
    codes=20 if not req else round(20*len(req&cc)/len(req))
    geo=10 if tender.get("scope")=="Federal" or not tender.get("province") or tender.get("province")==company.get("province") else 5
    cert=10 if company.get("certifications") else 0
    score=min(100,keyword+cat+codes+geo+cert)
    return {"fit":score,"keyword_hits":overlap[:8],"category_ok":cat>0,"code_matches":list(req&cc),
            "reason":f"{len(overlap)} capability hits • PEC category {'aligned' if cat else 'review required'}"}
def top_matches(company,tenders,min_fit=35,limit=50,categories=None,procedures=None):
    rows=[]
    for t in tenders:
        if categories and t.get("category") not in categories:continue
        if procedures and t.get("procedure") not in procedures:continue
        m=fit(company,t);x={**t,"match":m}
        if m["fit"]>=min_fit:rows.append(x)
    return sorted(rows,key=lambda x:(x.get("category",""),-x["match"]["fit"],x.get("deadline","")))[:limit]
