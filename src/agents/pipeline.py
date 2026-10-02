from src.scoring import assess
from src.rag.retriever import retrieve
from src.services.groq_service import analyze_tender
from src.services.pec_service import public_pec_check

def company_agent(company):
    fields=["company_name","email","pec_license","pec_category","pec_codes","ntn","province","years_experience","annual_turnover_m"]
    present=sum(bool(company.get(k)) for k in fields)
    return {"agent":"Company Digital Twin Agent","status":"complete","completeness":round(100*present/len(fields)),"missing":[k for k in fields if not company.get(k)]}

def pec_agent(company):
    return {"agent":"PEC Verification Agent","status":"human verification required","result":public_pec_check(company.get("company_name",""),company.get("pec_license",""))}

def document_agent(company,tender,text):
    evidence=retrieve(text,"mandatory eligibility PEC registration experience turnover bid security qualification deadline affidavit forms",6) if text else []
    ai=analyze_tender(company,tender,"\n\n".join(x["text"] for x in evidence)) if text else {"summary":"Upload the official tender document for evidence-grounded AI analysis.","risks":[],"next_steps":["Upload official PDF/DOCX."],"extracted_requirements":[]}
    return {"agent":"Document Intelligence Agent","status":"complete","evidence":evidence,"ai":ai}

def eligibility_agent(company,tender):
    return {"agent":"Eligibility Agent","status":"complete",**assess(company,tender)}

def compliance_agent(eligibility,ai):
    matrix=[{"requirement":x["criterion"],"status":x["status"],"evidence":x["evidence"],"action":"Retain evidence" if x["ok"] else "Resolve before submission"} for x in eligibility["checks"]]
    for r in ai.get("extracted_requirements",[])[:10]:
        matrix.append({"requirement":str(r),"status":"VERIFY","evidence":"AI extraction from tender","action":"Human confirmation required"})
    return {"agent":"Compliance Agent","status":"complete","matrix":matrix,"open_items":sum(x["status"]!="PASS" for x in matrix)}

def risk_agent(tender,eligibility,ai):
    risks=[f"Eligibility/evidence gap: {x}" for x in eligibility.get("gaps",[])]+[str(x) for x in ai.get("risks",[])][:8]
    if "corrigendum" in str(tender.get("status","")).lower(): risks.append("Corrigendum detected: compare latest official documents.")
    level="HIGH" if len(risks)>=4 else "MEDIUM" if risks else "LOW"
    return {"agent":"Risk Agent","status":"complete","risk_level":level,"risks":risks}

def strategy_agent(eligibility,risk):
    return {"agent":"Bid Strategy Agent","status":"complete","opportunity_fit":eligibility["fit"],
      "decision_support":"REVIEW" if eligibility["fit"]<80 or risk["risk_level"]=="HIGH" else "STRONG EVIDENCE ALIGNMENT",
      "actions":["Resolve mandatory gaps first.","Verify latest corrigendum and closing time.","Assign finance, technical and compliance owners.","Prepare bid security/forms strictly from official instructions."],
      "award_prediction":None}

def run_all(company,tender,text=""):
    log=[]
    c=company_agent(company); log.append(c)
    p=pec_agent(company); log.append(p)
    d=document_agent(company,tender,text); log.append({"agent":d["agent"],"status":d["status"]})
    e=eligibility_agent(company,tender); log.append({"agent":e["agent"],"status":e["status"]})
    co=compliance_agent(e,d["ai"]); log.append({"agent":co["agent"],"status":co["status"]})
    r=risk_agent(tender,e,d["ai"]); log.append({"agent":r["agent"],"status":r["status"]})
    s=strategy_agent(e,r); log.append({"agent":s["agent"],"status":s["status"]})
    return {"company":c,"pec":p,"document":d,"eligibility":e,"compliance":co,"risk":r,"strategy":s,"activity":log}
