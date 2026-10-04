from datetime import datetime
from src.agents.pipeline import run_all
STEPS=[
("Discovery Agent","Loads tender identity, jurisdiction, official URL and document evidence.","discovery"),
("PEC Verification Agent","Checks PEC category and specialization evidence.","eligibility"),
("Company Digital Twin Agent","Loads the selected persistent company profile.","company"),
("Document Intelligence Agent","Extracts tender requirements from the official document.","document"),
("Eligibility Agent","Evaluates eligibility gates and missing evidence.","eligibility"),
("Compliance Agent","Builds the compliance checklist.","compliance"),
("Risk Agent","Flags source, deadline and qualification risks.","risk"),
("Bid Strategy Agent","Produces bid-readiness guidance; never award probability.","strategy"),
("Final Report Agent","Consolidates the evidence-backed result.","summary")]
def _compact(v):
    if v is None:return "No structured output was produced for this step."
    if isinstance(v,dict):
        # readable short summary
        parts=[]
        for k,val in list(v.items())[:7]:
            if isinstance(val,(str,int,float,bool)):parts.append(f"{k.replace('_',' ').title()}: {val}")
            elif isinstance(val,list):parts.append(f"{k.replace('_',' ').title()}: {len(val)} item(s)")
        return " • ".join(parts)[:1200] or "Structured output completed."
    if isinstance(v,list):return f"{len(v)} item(s) produced."
    return str(v)[:1200]
def run_with_trace(company,tender,document_text=""):
    result=run_all(company,tender,document_text)
    trace=[];now=datetime.now().strftime("%H:%M:%S")
    for name,task,key in STEPS:
        if key=="company":
            out=f"{company.get('company_name','Company')} • PEC {company.get('pec_category','Unknown')} • {len(company.get('pec_codes',[]))} specialization code(s)"
        elif key=="discovery":
            out=f"{tender.get('title','Tender')} • {tender.get('province','')} • {tender.get('evidence_status','LIVE PUBLIC')} • source linked"
        elif key=="summary":
            out=f"Readiness {result.get('eligibility',{}).get('readiness','—')}% • Fit {result.get('eligibility',{}).get('fit','—')}% • Risk {result.get('risk',{}).get('risk_level','—')}"
        else:out=_compact(result.get(key) if isinstance(result,dict) else None)
        trace.append({"agent":name,"status":"complete","time":now,"task":task,"input":task,"output":out})
    return result,trace
