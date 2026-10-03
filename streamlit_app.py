import json
from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st
from src.config import DATA_DIR
from src.ui.components import hero,inject_v3_css
from src.ui.cards import tender_card
from src.services.live_discovery import federal_live,source_registry
from src.services.matcher import top_matches
from src.services.document_service import extract_text
from src.services.email_service import send_alert
from src.agents.pipeline import run_all
from src.db.supabase_store import health,save_company,save_tender,save_match,save_analysis,save_alert,count,recent
from src.reporting.report_builder import build_docx,build_pdf

st.set_page_config(page_title="TenderPulse AI",page_icon="⚡",layout="wide")
inject_v3_css();hero()
def load(n):return json.loads((DATA_DIR/n).read_text())
if "company" not in st.session_state:st.session_state.company=load("demo_company.json")
if "matches" not in st.session_state:st.session_state.matches=[]
if "selected_tender" not in st.session_state:st.session_state.selected_tender=None
company=st.session_state.company

with st.sidebar:
    st.markdown("## ⚡ TenderPulse")
    page=st.radio("Workspace",["🏠 Command Center","🏢 Company Profile","📡 Smart Tender Radar","🧠 Agentic Analysis","📋 Compliance & Reports","🗄 Database Inspector"])
    st.divider()
    h=health();st.caption(("🟢" if h.get("ok") else "🔴")+" Supabase "+h.get("status",""))
    st.caption("LIVE ≠ SIMULATION. Fit ≠ award probability.")

if page=="🏠 Command Center":
    st.subheader("Company-Specific Procurement Command Center")
    a,b,c,d=st.columns(4);a.metric("Matched opportunities",len(st.session_state.matches));b.metric("Company",company.get("pec_category","—"));c.metric("PEC codes",len(company.get("pec_codes",[])));d.metric("DB matches",count("matches"))
    st.info("Start with Company Profile. Then Smart Tender Radar discovers and ranks opportunities against that profile.")
    if st.session_state.matches:
        st.markdown("### Top opportunities")
        cols=st.columns(2)
        for i,t in enumerate(st.session_state.matches[:10]):
            with cols[i%2]:tender_card(t)

elif page=="🏢 Company Profile":
    st.subheader("Company Digital Twin")
    mode=st.radio("Profile type",["Test Company (pre-filled)","Real Company"],horizontal=True)
    if mode.startswith("Test"):
        if st.button("Load test C3 company"):
            st.session_state.company=load("demo_company.json");st.rerun()
    d=st.session_state.company
    pec_catalog=load("pec_codes.json")
    cert_options=["PEC Constructor Registration","NTN/FBR Registration","GST Registration","PRA Registration","SRB Registration","KPRA Registration","BRA Registration","SECP Registration","ISO 9001","ISO 14001","ISO 45001","Bank/Financial Certificate","Tax Active Taxpayer Evidence","Other"]
    with st.form("company"):
        c1,c2=st.columns(2)
        name=c1.text_input("Company name",d.get("company_name","") if mode.startswith("Test") else "")
        email=c2.text_input("Tender alert email",d.get("email","") if mode.startswith("Test") else "")
        c1,c2,c3=st.columns(3)
        lic=c1.text_input("PEC license / registration no.",d.get("pec_license","") if mode.startswith("Test") else "")
        cat=c2.selectbox("PEC category",["C-A","C-B","C1","C2","C3","C4","C5","C6"],index=["C-A","C-B","C1","C2","C3","C4","C5","C6"].index(d.get("pec_category","C3")))
        province=c3.selectbox("Home province / region",["Punjab","Sindh","Khyber Pakhtunkhwa","Balochistan","Federal","AJK","Gilgit-Baltistan"])
        codes=st.multiselect("PEC specialization codes",list(pec_catalog),default=[x for x in d.get("pec_codes",[]) if x in pec_catalog],format_func=lambda x:f"{x} — {pec_catalog[x]}")
        extra_codes=st.text_input("Other PEC codes (comma separated)","")
        certs=st.multiselect("Available registrations / certificates",cert_options,default=[x for x in d.get("certifications",[]) if x in cert_options])
        sectors=st.multiselect("Business sectors",["Civil Works","Roads","Buildings","Bridges","Water/Irrigation","Electrical","Solar","Mechanical","IT","Goods/Supplies","Consultancy"],default=[x for x in d.get("sectors",[]) if x in ["Civil Works","Roads","Buildings","Bridges","Water/Irrigation","Electrical","Solar","Mechanical","IT","Goods/Supplies","Consultancy"]])
        keywords=st.text_input("Company capability keywords",", ".join(d.get("keywords",[])))
        a,b,c=st.columns(3);exp=a.number_input("Experience (years)",0,80,int(d.get("years_experience",0)));turn=b.number_input("Annual turnover (PKR million)",0.0,1000000.0,float(d.get("annual_turnover_m",0)));largest=c.number_input("Largest completed project (PKR million)",0.0,1000000.0,float(d.get("largest_project_m",0)))
        if st.form_submit_button("Save Company Profile",type="primary"):
            allcodes=list(dict.fromkeys(codes+[x.strip().upper() for x in extra_codes.split(",") if x.strip()]))
            st.session_state.company={"mode":"TEST" if mode.startswith("Test") else "REAL","company_name":name,"email":email,"pec_license":lic,"pec_category":cat,"pec_codes":allcodes,"province":province,"certifications":certs,"sectors":sectors,"keywords":[x.strip() for x in keywords.split(",") if x.strip()],"years_experience":exp,"annual_turnover_m":turn,"largest_project_m":largest}
            r=save_company(st.session_state.company);st.success("Profile saved."+(" Supabase ✓" if r.get("ok") else " Session only — check Database Inspector."))
    st.link_button("Verify firm on official PEC","https://verification.pec.org.pk/")

elif page=="📡 Smart Tender Radar":
    st.subheader("Automatic Public Tender Discovery + Company Matching")
    scope=st.radio("Procurement scope",["Federal","Provincial"],horizontal=True)
    provinces=[]
    if scope=="Provincial":
        provinces=st.multiselect("Select province(s)",["Punjab","Sindh","Khyber Pakhtunkhwa","Balochistan"],default=[company.get("province","Punjab")] if company.get("province") in ["Punjab","Sindh","Khyber Pakhtunkhwa","Balochistan"] else ["Punjab"])
    c1,c2,c3=st.columns(3);minfit=c1.slider("Minimum fit %",0,100,35,5);pages=c2.slider("Federal pages to scan",1,10,3);topn=c3.selectbox("Show top", [10,20,30],index=0)
    scan_date=st.date_input("Tender radar date",date.today())
    if st.button("🔎 Discover & Match Tenders",type="primary"):
        found=[]
        if scope=="Federal":
            with st.spinner("Reading Federal PPRA public active tenders…"):found=federal_live(pages)
        else:
            st.warning("Provincial portals use different public interfaces. V3 exposes official sources and uses normalized simulation until a connector passes live parsing checks.")
            demo=load("demo_tenders.json")
            found=[{**x,"scope":"Provincial","province":x.get("province") or x.get("region",""),"status":"SIMULATION"} for x in demo if (not provinces or (x.get("province") or x.get("region","")) in provinces)]
        matches=top_matches(company,found,minfit,topn);st.session_state.matches=matches
        for t in matches:
            save_tender(t);save_match(company,t,t["match"]["fit"],t["match"])
        st.success(f"Scanned {len(found)} normalized records; showing {len(matches)} profile matches.")
    if scope=="Provincial":
        st.markdown("**Official source links**")
        for p,u in source_registry().items():
            if p in provinces:st.link_button(f"Open {p} procurement source",u)
    if st.session_state.matches:
        st.markdown(f"### Top {min(topn,len(st.session_state.matches))} matched tenders")
        cols=st.columns(2)
        for i,t in enumerate(st.session_state.matches[:topn]):
            with cols[i%2]:
                tender_card(t)
                if st.button("Analyze this tender",key=f"a_{t['id']}_{i}"):
                    st.session_state.selected_tender=t;st.success("Selected. Open Agentic Analysis.")

elif page=="🧠 Agentic Analysis":
    st.subheader("Evidence-Grounded Agentic Analysis")
    t=st.session_state.selected_tender
    if not t:st.info("Select a matched tender in Smart Tender Radar first.")
    else:
        tender_card(t)
        up=st.file_uploader("Upload official tender PDF/DOCX/TXT for deep analysis",type=["pdf","docx","txt"])
        if st.button("▶ Run Agents",type="primary"):
            txt=extract_text(up) if up else ""
            with st.status("Running procurement intelligence agents…",expanded=True) as status:
                st.write("Company Digital Twin → PEC → Documents/RAG → Eligibility → Compliance → Risk → Strategy")
                r=run_all(company,t,txt);st.session_state.result=r
                db=save_analysis(t.get("id"),company.get("company_name"),r)
                status.update(label="Analysis complete",state="complete")
            a,b,c=st.columns(3);a.metric("Readiness",f"{r['eligibility']['readiness']}%");b.metric("Opportunity Fit",f"{r['eligibility']['fit']}%");c.metric("Risk",r["risk"]["risk_level"])
            if db.get("ok"):st.toast("Saved to Supabase")

elif page=="📋 Compliance & Reports":
    st.subheader("Compliance, Report & Alert")
    if "result" not in st.session_state:st.info("Run Agentic Analysis first.")
    else:
        r=st.session_state.result;t=st.session_state.selected_tender
        st.dataframe(pd.DataFrame(r["compliance"]["matrix"]),hide_index=True,use_container_width=True)
        a,b=st.columns(2);a.download_button("Download DOCX",build_docx(company,t,r),file_name=f"{t['id']}_report.docx");b.download_button("Download PDF",build_pdf(company,t,r),file_name=f"{t['id']}_report.pdf")
        recipient=st.text_input("Alert recipient",company.get("email",""))
        if st.button("Send email now"):
            ok,msg=send_alert(recipient,f"TenderPulse AI | {t['id']}",f"{t['title']}\nFit: {t['match']['fit']}%\nDeadline: {t.get('deadline')}\nRisk: {r['risk']['risk_level']}\nVerify the official tender before bidding.")
            save_alert(t["id"],recipient,"sent" if ok else "failed");st.success(msg) if ok else st.error(msg)
        st.info("Daily 8:00 AM delivery must run from a cloud scheduler, not the Streamlit page. See DAILY_8AM_AUTOMATION.md.")

elif page=="🗄 Database Inspector":
    st.subheader("Supabase Persistence Inspector")
    h=health();st.json(h)
    cols=st.columns(5)
    for c,t in zip(cols,["companies","tenders","matches","analyses","alerts"]):c.metric(t.title(),count(t))
    table=st.selectbox("Inspect recent records",["companies","tenders","matches","analyses","alerts"])
    rows=recent(table,10)
    st.dataframe(pd.DataFrame(rows),use_container_width=True) if rows else st.warning("No rows found. Run/save the relevant workflow and check schema migration.")
