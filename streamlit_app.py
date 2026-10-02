import json
import pandas as pd
import plotly.express as px
import streamlit as st
from src.config import DATA_DIR
from src.ui.components import hero, process, next_action
from src.scoring import assess
from src.simulation import national_simulation, yearly_company_demo
from src.services.groq_service import analyze_tender, available as groq_available
from src.services.document_service import extract_text
from src.services.email_service import send_alert, configured as email_configured
from src.services.pec_service import public_pec_check
from src.services.tender_sources import source_health, federal_public_preview, SOURCE_DIRECTORY

st.set_page_config(page_title="TenderPulse AI",page_icon="⚡",layout="wide")
hero()

def load(name):
    return json.loads((DATA_DIR/name).read_text(encoding="utf-8"))
if "company" not in st.session_state: st.session_state.company=load("demo_company.json")
if "tenders" not in st.session_state: st.session_state.tenders=load("demo_tenders.json")
if "selected" not in st.session_state: st.session_state.selected=0

tabs=st.tabs(["Command Center","Company Twin","Tender Radar","AI Analysis","Compliance","Simulation","Alerts"])

with tabs[0]:
    process(1)
    company=st.session_state.company
    tender=st.session_state.tenders[st.session_state.selected]
    a=assess(company,tender)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Demo opportunities",len(st.session_state.tenders))
    c2.metric("Selected bid readiness",f'{a["readiness"]}%')
    c3.metric("Opportunity fit",f'{a["fit"]}%')
    c4.metric("Groq","Connected" if groq_available() else "Add API key")
    st.warning("Simulation/demo metrics are synthetic. Opportunity Fit measures supplied evidence alignment and is NOT an award/win probability.")
    sim=national_simulation()
    st.plotly_chart(px.bar(sim,x="Region",y="Simulated opportunities",title="Pakistan Opportunity Radar — SIMULATION"),use_container_width=True)
    next_action("Complete the Company Digital Twin","Review the demo profile, replace it with your firm's real non-sensitive business information, then run PEC public-source verification.")

with tabs[1]:
    process(1)
    d=st.session_state.company
    st.caption("Pre-filled with synthetic hackathon data. Replace it for a real demonstration.")
    with st.form("company"):
        name=st.text_input("Company name",d["company_name"])
        email=st.text_input("Tender alert email",d["email"])
        c1,c2,c3=st.columns(3)
        lic=c1.text_input("PEC license",d["pec_license"])
        cat=c2.selectbox("PEC category",["C-A","C-B","C1","C2","C3","C4","C5","C6"],index=4)
        codes=c3.text_input("PEC codes (comma separated)",",".join(d["pec_codes"]))
        province=st.selectbox("Province / region",["Punjab","Sindh","Khyber Pakhtunkhwa","Balochistan","Federal","AJK","Gilgit-Baltistan"])
        exp=st.number_input("Experience (years)",0,50,int(d["years_experience"]))
        turnover=st.number_input("Annual turnover (PKR million)",0.0,100000.0,float(d["annual_turnover_m"]))
        if st.form_submit_button("Save Company Twin",type="primary"):
            d.update(company_name=name,email=email,pec_license=lic,pec_category=cat,pec_codes=[x.strip() for x in codes.split(",") if x.strip()],province=province,years_experience=exp,annual_turnover_m=turnover)
            st.session_state.company=d; st.success("Company Twin updated.")
    if st.button("Verify against PEC public source"):
        st.session_state.pec=public_pec_check(name,lic)
    if "pec" in st.session_state: st.json(st.session_state.pec)
    st.link_button("Open official PEC Constructor/Operator Portal","https://coportal.pec.org.pk/")

with tabs[2]:
    process(2)
    st.subheader("Public-source radar")
    cols=st.columns(2)
    if cols[0].button("Check Pakistan procurement source health"):
        st.session_state.health=source_health()
    if cols[1].button("Preview Federal PPRA public feed"):
        st.session_state.fed=federal_public_preview()
    if "health" in st.session_state: st.dataframe(pd.DataFrame(st.session_state.health),use_container_width=True,hide_index=True)
    if "fed" in st.session_state:
        st.success("Federal public page reached.") if st.session_state.fed["ok"] else st.error(st.session_state.fed["note"])
        st.text_area("Live public page preview",st.session_state.fed["preview"],height=180)
    st.subheader("Normalized hackathon tenders — SIMULATION")
    options=[f'{t["id"]} • {t["title"]}' for t in st.session_state.tenders]
    choice=st.selectbox("Select opportunity",options,index=st.session_state.selected)
    st.session_state.selected=options.index(choice)
    t=st.session_state.tenders[st.session_state.selected]
    st.json(t)
    next_action("Analyze the selected opportunity","Upload the actual tender PDF/DOCX in AI Analysis, or run Groq against the structured demo tender.")

with tabs[3]:
    process(3)
    t=st.session_state.tenders[st.session_state.selected]
    up=st.file_uploader("Tender document (PDF, DOCX, TXT)",type=["pdf","docx","txt"])
    text=extract_text(up) if up else ""
    if text: st.caption(f"Extracted {len(text):,} characters.")
    if st.button("Run Groq Tender Intelligence",type="primary"):
        with st.spinner("Agent is extracting requirements, risks and next actions..."):
            try: st.session_state.ai=analyze_tender(st.session_state.company,t,text)
            except Exception as e: st.session_state.ai={"error":str(e)}
    if "ai" in st.session_state: st.json(st.session_state.ai)
    next_action("Open the compliance matrix","Confirm hard requirements using source documents; do not rely on an LLM statement alone.")

with tabs[4]:
    process(4)
    t=st.session_state.tenders[st.session_state.selected]
    a=assess(st.session_state.company,t)
    c1,c2=st.columns(2)
    c1.metric("Bid Readiness",f'{a["readiness"]}%')
    c2.metric("Opportunity Fit",f'{a["fit"]}%')
    st.dataframe(pd.DataFrame(a["checks"]),use_container_width=True,hide_index=True)
    if a["gaps"]: st.error("Evidence/eligibility gaps: "+", ".join(a["gaps"]))
    else: st.success("No gaps detected in this simplified demo rule set. Human verification is still required.")
    next_action("Resolve gaps, then notify the company","The alert can summarize the selected tender, readiness and outstanding evidence.")

with tabs[5]:
    process(4)
    st.warning("All charts on this page are explicitly synthetic live simulations for hackathon demonstration.")
    nat=national_simulation()
    st.plotly_chart(px.scatter(nat,x="Simulated opportunities",y="Avg readiness",size="Matched",color="Region",title="National Opportunity vs Readiness — SIMULATION"),use_container_width=True)
    yr=yearly_company_demo()
    st.plotly_chart(px.line(yr,x="Year",y=["Bids","Qualified","Awards"],markers=True,title="Company Bid Pipeline 2022–2026 — SYNTHETIC"),use_container_width=True)
    st.plotly_chart(px.bar(yr,x="Year",y="Revenue (PKR m)",title="Annual Procurement Revenue — SYNTHETIC"),use_container_width=True)

with tabs[6]:
    process(5)
    t=st.session_state.tenders[st.session_state.selected]
    a=assess(st.session_state.company,t)
    recipient=st.text_input("Recipient",st.session_state.company["email"])
    body=f"""TenderPulse AI opportunity alert

Company: {st.session_state.company['company_name']}
Tender: {t['title']}
Agency: {t['agency']}
Deadline: {t['deadline']}
Bid readiness: {a['readiness']}%
Opportunity fit: {a['fit']}%
Gaps: {', '.join(a['gaps']) if a['gaps'] else 'None detected by simplified rule engine'}

Important: readiness/fit are evidence-alignment indicators, not award predictions. Verify the official tender and PEC/procurement requirements before submission.
"""
    st.text_area("Email preview",body,height=260)
    if st.button("Send company alert",type="primary"):
        ok,msg=send_alert(recipient,f"TenderPulse AI | {t['id']} | Action Required",body)
        st.success(msg) if ok else st.error(msg)
    st.caption("SMTP status: configured" if email_configured() else "SMTP not configured. Add secrets to enable sending.")
