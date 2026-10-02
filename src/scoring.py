CATEGORY_RANK={"C-A":9,"C-B":8,"C-1":7,"C1":7,"C-2":6,"C2":6,"C-3":5,"C3":5,"C-4":4,"C4":4,"C-5":3,"C5":3,"C-6":2,"C6":2}

def assess(company, tender):
    checks=[]
    def add(name, ok, evidence, weight):
        checks.append({"criterion":name,"status":"PASS" if ok else "GAP","evidence":evidence,"weight":weight,"ok":ok})
    cr=CATEGORY_RANK.get(company.get("pec_category",""),0)
    tr=CATEGORY_RANK.get(tender.get("min_category",""),0)
    add("PEC category", cr>=tr and cr>0, f'{company.get("pec_category")} vs required {tender.get("min_category")}', 25)
    required=set(tender.get("required_codes",[])); owned=set(company.get("pec_codes",[]))
    add("PEC specialization", required.issubset(owned), f'Have {sorted(owned)}; required {sorted(required)}', 25)
    add("Experience", company.get("years_experience",0)>=tender.get("min_experience",0), f'{company.get("years_experience")}y vs {tender.get("min_experience")}y', 20)
    add("Turnover", company.get("annual_turnover_m",0)>=tender.get("min_turnover_m",0), f'PKR {company.get("annual_turnover_m")}m vs {tender.get("min_turnover_m")}m', 20)
    add("Basic certification evidence", bool(company.get("certifications")), ", ".join(company.get("certifications",[])) or "None supplied", 10)
    score=sum(x["weight"] for x in checks if x["ok"])
    gaps=[x["criterion"] for x in checks if not x["ok"]]
    return {"readiness":score,"fit":min(100, score + (5 if company.get("province")==tender.get("province") else 0)),"checks":checks,"gaps":gaps}
