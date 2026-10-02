import json,time
import pandas as pd
import plotly.express as px
import streamlit as st
from src.config import DATA_DIR
from src.ui.components import hero,next_action
from src.services.document_service import extract_text
from src.services.tender_sources import source_health,federal_public_preview
from src.services.email_service import send_alert,configured as smtp_ready
from src.agents.pipeline import run_all
from src.agents.corrigendum_agent import fingerprint
from src.reporting.report_builder import build_docx,build_pdf
from src.db.supabase_store import health as db_health

st.set_page_config(page_title="TenderPulse AI",page_icon="⚡",layout="wide")
hero()
def load(n):return json.loads((DATA_DIR/n).read_text(encoding="utf-8"))
if "company" not in st.session_state:st.session_state.company=load("demo_company.json")
if "tenders" not in st.session_state:st.session_state.tenders=load("demo_tenders.json")
if "selected" not in st.session_state:st.session_state.selected=0

with st.sidebar:
    st.markdown("### ⚡ TenderPulse")
    page=st.radio("Workspace",["Command Center","Company Twin","Tender Radar","Agentic Analysis","Compliance & Risk","Corrigendum Watch","Reports & Alerts","National Simulation"])
    st.divider();st.caption("2026 Hackathon Build")
    st.json(db_health(),expanded=False)

company=st.session_state.company;tender=st.session_state.tenders[st.session_state.selected]

if page=="Command Center":
    st.subheader("National Procurement Intelligence Command Center")
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Demo opportunities",len(st.session_state.tenders));c2.metric("Regions",7);c3.metric("Agents",7);c4.metric("Mode","Cloud-ready")
    st.warning("Live public-source results, AI inference and synthetic simulation are explicitly separated. Scores are evidence-alignment indicators, not award predictions.")
    from src.simulation import national_simulation,yearly_company_demo
    nat=national_simulation();st.plotly_chart(px.bar(nat,x="Region",y=["Simulated opportunities","Matched"],barmode="group",title="Pakistan Opportunity Radar — SIMULATION"),use_container_width=True)
    next_action("Build the Company Digital Twin","Review the synthetic profile, then use Tender Radar and Agentic Analysis.")

elif page=="Company Twin":
    st.subheader("Company Digital Twin + PEC Evidence")
    st.caption("Synthetic data is pre-filled for the hackathon.")
    d=company
    with st.form("cp"):
        name=st.text_input("Company",d["company_name"]);email=st.text_input("Alert email",d["email"])
        a,b,c=st.columns(3);lic=a.text_input("PEC license",d["pec_license"]);cat=b.selectbox("PEC category",["C-A","C-B","C1","C2","C3","C4","C5","C6"],index=4);codes=c.text_input("PEC codes",",".join(d["pec_codes"]))
        province=st.selectbox("Region",["Punjab","Sindh","Khyber Pakhtunkhwa","Balochistan","Federal","AJK","Gilgit-Baltistan"])
        exp=st.number_input("Experience years",0,50,int(d["years_experience"]));turn=st.number_input("Annual turnover PKR m",0.0,100000.0,float(d["annual_turnover_m"]))
        if st.form_submit_button("Save Digital Twin",type="primary"):
            d.update(company_name=name,email=email,pec_license=lic,pec_category=cat,pec_codes=[x.strip() for x in codes.split(",") if x.strip()],province=province,years_experience=exp,annual_turnover_m=turn);st.session_state.company=d;st.success("Saved.")
    st.info("PEC's public firm-verification flow uses CAPTCHA. TenderPulse therefore requires human confirmation rather than bypassing it.")
    st.link_button("Open official PEC Firm Verification","https://verification.pec.org.pk/")

elif page=="Tender Radar":
    st.subheader("Tender Discovery Agent")
    a,b=st.columns(2)
    if a.button("Check Pakistan source health"):st.session_state.health=source_health()
    if b.button("Read Federal PPRA public page"):st.session_state.fed=federal_public_preview()
    if "health" in st.session_state:st.dataframe(pd.DataFrame(st.session_state.health),hide_index=True,use_container_width=True)
    if "fed" in st.session_state:st.text_area("LIVE public Federal PPRA preview",st.session_state.fed["preview"],height=220)
    st.markdown("#### Normalized opportunities — SIMULATION")
    opts=[f"{x['id']} • {x['title']}" for x in st.session_state.tenders];choice=st.selectbox("Opportunity",opts,index=st.session_state.selected);st.session_state.selected=opts.index(choice);tender=st.session_state.tenders[st.session_state.selected]
    st.json(tender);st.caption("Fingerprint: "+fingerprint(tender))

elif page=="Agentic Analysis":
    st.subheader("Live Agent Activity")
    up=st.file_uploader("Official tender PDF/DOCX/TXT",type=["pdf","docx","txt"]);txt=extract_text(up) if up else ""
    if st.button("▶ Run Full Agentic Workflow",type="primary"):
        box=st.empty();events=["Company Digital Twin Agent","PEC Verification Agent","Document Intelligence Agent","Eligibility Agent","Compliance Agent","Risk Agent","Bid Strategy Agent"]
        for i,x in enumerate(events):box.info(f"Agent {i+1}/{len(events)} — {x} running…");time.sleep(.12)
        try:st.session_state.result=run_all(company,tender,txt);box.success("Agent workflow completed.")
        except Exception as e:box.error(str(e))
    if "result" in st.session_state:
        r=st.session_state.result
        for x in r["activity"]:st.success(f"✓ {x['agent']} — {x['status']}")
        c1,c2,c3=st.columns(3);c1.metric("Bid Readiness",f"{r['eligibility']['readiness']}%");c2.metric("Opportunity Fit",f"{r['eligibility']['fit']}%");c3.metric("Risk",r["risk"]["risk_level"])
        st.json(r["document"]["ai"])

elif page=="Compliance & Risk":
    st.subheader("Compliance Matrix + Risk Agent")
    if "result" not in st.session_state:st.info("Run Agentic Analysis first.")
    else:
        r=st.session_state.result;st.dataframe(pd.DataFrame(r["compliance"]["matrix"]),hide_index=True,use_container_width=True)
        st.metric("Open items",r["compliance"]["open_items"]);st.write("**Risk level:**",r["risk"]["risk_level"])
        for x in r["risk"]["risks"]:st.warning(x)
        st.write("**Bid Strategy:**",r["strategy"]["decision_support"])
        for x in r["strategy"]["actions"]:st.write("→",x)

elif page=="Corrigendum Watch":
    st.subheader("Corrigendum & Deadline Watch")
    st.metric("Current tender fingerprint",fingerprint(tender));st.write("Deadline:",tender["deadline"])
    st.info("Production mode stores prior fingerprints and alerts when official metadata/documents change. Federal PPRA publicly marks corrigenda; this hackathon build demonstrates the comparison architecture.")
    st.code('old = {"deadline":"2026-10-20","security_m":1.0}\nnew = {"deadline":"2026-10-27","security_m":1.5}\n→ deadline changed; bid security changed')

elif page=="Reports & Alerts":
    st.subheader("Final Bid Intelligence Report Agent")
    if "result" not in st.session_state:st.info("Run Agentic Analysis first.")
    else:
        r=st.session_state.result
        docx=build_docx(company,tender,r);pdf=build_pdf(company,tender,r)
        a,b=st.columns(2);a.download_button("Download DOCX Report",docx,file_name=f"{tender['id']}_TenderPulse_Report.docx");b.download_button("Download PDF Report",pdf,file_name=f"{tender['id']}_TenderPulse_Report.pdf")
        body=f"""TenderPulse AI Alert\n\n{tender['title']}\nDeadline: {tender['deadline']}\nReadiness: {r['eligibility']['readiness']}%\nFit: {r['eligibility']['fit']}%\nRisk: {r['risk']['risk_level']}\nGaps: {', '.join(r['eligibility']['gaps']) or 'None detected'}\n\nNot an award prediction. Verify official documents."""
        recipient=st.text_input("Company recipient",company["email"]);st.text_area("Email preview",body,height=220)
        if st.button("Send Alert Email",type="primary"):
            ok,msg=send_alert(recipient,f"TenderPulse AI | {tender['id']}",body);st.success(msg) if ok else st.error(msg)
        st.caption("SMTP configured." if smtp_ready() else "Add SMTP secrets to enable real email sending.")

elif page=="National Simulation":
    st.subheader("Pakistan-wide Live Simulation")
    st.warning("SYNTHETIC hackathon simulation — not official procurement statistics.")
    from src.simulation import national_simulation,yearly_company_demo
    n=national_simulation();y=yearly_company_demo()
    st.plotly_chart(px.scatter(n,x="Simulated opportunities",y="Avg readiness",size="Matched",color="Region",title="Regional Opportunity vs Readiness — SIMULATION"),use_container_width=True)
    st.plotly_chart(px.line(y,x="Year",y=["Bids","Qualified","Awards"],markers=True,title="Company Procurement Progress — SYNTHETIC"),use_container_width=True)
    st.plotly_chart(px.bar(y,x="Year",y="Revenue (PKR m)",title="Yearly Procurement Revenue — SYNTHETIC"),use_container_width=True)
