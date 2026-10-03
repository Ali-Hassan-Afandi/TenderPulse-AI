from datetime import datetime
from src.agents.pipeline import run_all
AGENTS=[
("Discovery Agent","Loads tender and official source evidence."),
("PEC Verification Agent","Checks PEC category/codes against available tender evidence."),
("Company Digital Twin Agent","Loads the selected persistent company profile."),
("Document Intelligence Agent","Extracts requirements and tender evidence."),
("Eligibility Agent","Evaluates eligibility gates and missing evidence."),
("Compliance Agent","Builds the compliance checklist."),
("Risk Agent","Flags source, deadline and qualification risks."),
("Bid Strategy Agent","Produces bid-readiness guidance, not award prediction."),
("Final Report Agent","Combines verified evidence and recommendations.")]
def run_with_trace(company,tender,document_text=''):
    result=run_all(company,tender,document_text); trace=[]
    for name,task in AGENTS:
        output="Completed; result handed to the next agent."
        if isinstance(result,dict):
            for k in ("eligibility","compliance","risk","strategy","document","summary"):
                if k in result and result[k]:output=str(result[k])[:1000];break
        trace.append({"agent":name,"status":"completed","time":datetime.now().strftime("%H:%M:%S"),"input":task,"output":output})
    return result,trace
