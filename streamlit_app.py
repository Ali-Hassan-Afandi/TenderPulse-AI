import json
from datetime import date,timedelta
import pandas as pd
import plotly.express as px
import streamlit as st
from src.config import DATA_DIR
from src.ui.components import hero,inject_v3_css,progress_header
from src.ui.cards import tender_card
from src.services.live_discovery import discover,source_registry
from src.services.matcher import top_matches
from src.services.document_service import extract_text
from src.services.email_service import send_alert
from src.agents.pipeline import run_all
from src.db.supabase_store import health,save_company,save_tender,save_match,save_analysis,save_alert,count,recent
from src.reporting.report_builder import build_docx,build_pdf
from src.simulation import national_simulation,yearly_company_demo
from src.services.profile_analytics import completeness,yearly_progress,seven_day_matches

st.set_page_config(page_title="TenderPulse AI",page_icon="⚡",layout="wide")
inject_v3_css();hero()
PAGES=["🏠 Command Center","🏢 Company Profile","📡 Tender Radar","🧠 Agentic Analysis","📋 Compliance & Reports","🗄 Database Inspector"]
def load(n):return json.loads((DATA_DIR/n).read_text())
if "company" not in st.session_state:st.session_state.company=load("demo_company.json")
if "matches" not in st.session_state:st.session_state.matches=[]
if "selected_tender" not in st.session_state:st.session_state.selected_tender=None
if "page" not in st.session_state:st.session_state.page=PAGES[0]
company=st.session_state.company

with st.sidebar:
    st.markdown("## ⚡ TenderPulse")
    idx=PAGES.index(st.session_state.page) if st.session_state.page in PAGES else 0
    page=st.radio("Workspace",PAGES,index=idx)
    st.session_state.page=page
    step=PAGES.index(page)+1;progress_header(step,len(PAGES),page.split(" ",1)[1])
    h=health();st.caption(("🟢" if h.get("ok") else "🔴")+" Supabase "+h.get("status",""))
    st.caption("Fit = evidence alignment, not award probability.")

def go(p):
    st.session_state.page=p;st.rerun()

if page=="🏠 Command Center":
    st.subheader("Live Procurement Intelligence Command Center")
    a,b,c,d=st.columns(4);a.metric("Current matches",len(st.session_state.matches));b.metric("PEC category",company.get("pec_category","—"));c.metric("PEC codes",len(company.get("pec_codes",[])));d.metric("Stored matches",count("matches"))
    st.markdown("### 📅 Date-wise Opportunity Simulation")
    st.caption("SIMULATION — visual demo of how daily matched opportunities will appear when live connectors are normalized.")
    sim=load("demo_tenders.json")
    for i,t in enumerate(sim[:10]):
        t={**t,"id":t.get("id",f"SIM-{i+1}"),"scope":t.get("scope","Pakistan"),"province":t.get("province",""),"category":t.get("category","Works"),"procedure":t.get("procedure","SS1E"),"deadline":t.get("deadline",str(date.today()+timedelta(days=i+3))),"source_url":"#","match":{"fit":max(48,94-i*4),"reason":"Synthetic company-fit demonstration"}}
        cols=st.columns([1,5,1])
        cols[0].markdown(f"**{(date.today()+timedelta(days=i)).strftime('%d %b')}**")
        with cols[1]:tender_card(t)
        cols[2].metric("Fit",f"{t['match']['fit']}%")
    st.markdown("### Company Progress")
    p1,p2=st.columns([1,2])
    p1.metric("Profile completeness",f"{completeness(company)}%")
    p1.progress(completeness(company)/100)
    yp=yearly_progress(company)
    p2.plotly_chart(px.line(yp,x="Year",y=["Capability Index","Turnover Index","Project Index"],markers=True,title="5-Year Company Improvement — SIMULATION"),use_container_width=True)
    st.markdown("### Last 7 Days — Matching Tender Trend")
    sd=seven_day_matches()
    st.plotly_chart(px.bar(sd,x="Date",y="Matches",color="Category",barmode="group",title="Matched tenders by procurement category — SIMULATION"),use_container_width=True)
    st.markdown("### National simulation")
    nat=national_simulation();st.plotly_chart(px.bar(nat,x="Region",y=["Simulated opportunities","Matched"],barmode="group"),use_container_width=True)
    if st.button("Next → Build Company Profile",type="primary",use_container_width=True):go("🏢 Company Profile")

elif page=="🏢 Company Profile":
    st.subheader("Company Digital Twin")
    mode=st.radio("Profile type",["Test Company (pre-filled)","Real Company"],horizontal=True,key="profile_type_mode")
    if mode.startswith("Test") and st.button("Load Test C3 Company"):st.session_state.company=load("demo_company.json");st.rerun()
    d=st.session_state.company;codes_catalog=load("pec_codes.json")
    certs_all=["PEC Constructor Registration","NTN/FBR Registration","GST Registration","PRA Registration","SRB Registration","KPRA Registration","BRA Registration","SECP Registration","ISO 9001","ISO 14001","ISO 45001","Bank/Financial Certificate","Active Taxpayer Evidence","Other"]
    with st.form("company_profile_form",clear_on_submit=False):
        a,b=st.columns(2)
        name=a.text_input("Company name",d.get("company_name","") if mode.startswith("Test") else "",key="company_name_input")
        email=b.text_input("Tender alert email",d.get("email","") if mode.startswith("Test") else "",key="company_email_input")
        a,b,c=st.columns(3)
        lic=a.text_input("PEC registration no.",d.get("pec_license","") if mode.startswith("Test") else "",key="pec_license_input")
        _cats=["C-A","C-B","C1","C2","C3","C4","C5","C6"]; _cat=d.get("pec_category","C3")
        cat=b.selectbox("PEC category",_cats,index=_cats.index(_cat) if _cat in _cats else 4,key="pec_category_input")
        _regions=["Punjab","Sindh","Khyber Pakhtunkhwa","Balochistan","Federal","AJK","Gilgit-Baltistan"]; _reg=d.get("province","Punjab")
        province=c.selectbox("Home region",_regions,index=_regions.index(_reg) if _reg in _regions else 0,key="home_region_input")
        codes=st.multiselect("PEC specialization codes — searchable official catalog",list(codes_catalog),default=[x for x in d.get("pec_codes",[]) if x in codes_catalog],format_func=lambda x:f"{x} — {codes_catalog[x]}",key="pec_codes_input",help="Search by code or description. Verify final firm codes on PEC.")
        certs=st.multiselect("Available registrations / certificates",certs_all,default=[x for x in d.get("certifications",[]) if x in certs_all],key="certificates_input")
        sectors=st.multiselect("Business sectors",["Civil Works","Roads","Buildings","Bridges","Water/Irrigation","Electrical","Solar","Mechanical","IT","Goods/Supplies","Consultancy"],default=[x for x in d.get("sectors",[]) if x in ["Civil Works","Roads","Buildings","Bridges","Water/Irrigation","Electrical","Solar","Mechanical","IT","Goods/Supplies","Consultancy"]],key="sectors_input")
        kw=st.text_input("Capability keywords",", ".join(d.get("keywords",[])),key="capability_keywords_input")
        a,b=st.columns(2)
        exp=a.number_input("Experience years",0,80,int(d.get("years_experience",0)),key="experience_input")
        turn=b.number_input("Annual turnover PKR million",0.0,1000000.0,float(d.get("annual_turnover_m",0)),key="turnover_input")
        if st.form_submit_button("Save Company Profile",type="primary",use_container_width=True):
            st.session_state.company={"mode":"TEST" if mode.startswith("Test") else "REAL","company_name":name,"email":email,"pec_license":lic,"pec_category":cat,"pec_codes":codes,"province":province,"certifications":certs,"sectors":sectors,"keywords":[x.strip() for x in kw.split(",") if x.strip()],"years_experience":exp,"annual_turnover_m":turn}
            r=save_company(st.session_state.company);st.success("Saved to Supabase." if r.get("ok") else "Saved in session; inspect Supabase connection.")
    st.markdown("### Profile Progress")
    _pc=completeness(st.session_state.company)
    st.progress(_pc/100,text=f"{_pc}% company profile complete")
    st.caption("A richer verified profile improves tender filtering: PEC codes, certificates, sectors, experience and turnover all matter.")
    st.link_button("Verify on official PEC","https://verification.pec.org.pk/")
    if st.button("Next → Search Matching Tenders",type="primary",use_container_width=True):go("📡 Tender Radar")

elif page=="📡 Tender Radar":
    st.subheader("Pakistan Public Tender Radar")
    regions=st.multiselect("Search jurisdictions",["Federal","Punjab","Sindh","Khyber Pakhtunkhwa","Balochistan","AJK","Gilgit-Baltistan"],default=["Federal"])
    categories=st.multiselect("Procurement category",["Works","Goods","Non-Consultancy Services","Consultancy Services","Other"],default=["Works","Goods","Non-Consultancy Services","Consultancy Services"])
    procedures=st.multiselect("Procurement procedure",["SS1E","SS2E","Other/Unspecified"],default=["SS1E","SS2E","Other/Unspecified"],help="SS1E = Single Stage–One Envelope; SS2E = Single Stage–Two Envelope.")
    a,b,c=st.columns(3);minfit=a.slider("Minimum company fit",0,100,30,5);pages=b.slider("Federal pages",1,10,3);topn=c.selectbox("Results",[10,20,30,50])
    registry=source_registry()
    with st.expander("Official procurement sources"):
        for r in regions:st.link_button(f"Open {r} official source ↗",registry[r])
    if st.button("🔎 Search Open Sources & Match Company",type="primary"):
        live_regions=[r for r in regions if r in ["Federal","AJK","Gilgit-Baltistan"]]
        with st.spinner("Reading supported public sources…"):found=discover(live_regions,pages)
        # clearly-labelled simulation fallback for connectors not yet normalized
        unsupported=[r for r in regions if r not in live_regions]
        if unsupported:
            demo=load("demo_tenders.json")
            for region in unsupported:
                for i,x in enumerate(demo[:5]):
                    found.append({**x,"id":f"SIM-{region[:3].upper()}-{i+1}","scope":"Provincial","province":region,"status":"SIMULATION","source":registry[region],"source_url":registry[region],"category":x.get("category","Works"),"procedure":x.get("procedure","Other/Unspecified")})
            st.warning("Simulation fallback used for: "+", ".join(unsupported)+". Official source buttons are provided; these records are not represented as live.")
        matches=top_matches(st.session_state.company,found,minfit,topn,categories,procedures);st.session_state.matches=matches
        for t in matches:save_tender(t);save_match(st.session_state.company,t,t["match"]["fit"],t["match"])
        st.success(f"{len(found)} normalized records scanned → {len(matches)} company matches.")
    if st.session_state.matches:
        cats={}
        for t in st.session_state.matches:cats.setdefault(t.get("category","Other"),[]).append(t)
        for cat,items in cats.items():
            st.markdown(f"### {cat} ({len(items)})")
            cols=st.columns(2)
            for i,t in enumerate(items):
                with cols[i%2]:
                    tender_card(t)
                    if st.button("Select for AI analysis",key=f"sel_{cat}_{i}_{t['id']}"):st.session_state.selected_tender=t;st.success("Selected.")
    if st.button("Next → Analyze Selected Tender",type="primary",use_container_width=True):go("🧠 Agentic Analysis")

elif page=="🧠 Agentic Analysis":
    st.subheader("Agentic Tender Analysis")
    t=st.session_state.selected_tender
    if not t:st.warning("Select a tender in Tender Radar first.")
    else:
        tender_card(t);up=st.file_uploader("Upload official PDF/DOCX/TXT for evidence-grounded analysis",type=["pdf","docx","txt"])
        if st.button("▶ Run Analysis Agents",type="primary"):
            txt=extract_text(up) if up else ""
            with st.status("Executing agents…",expanded=True) as status:
                for x in ["Company Digital Twin","PEC Verification","Document/RAG","Eligibility","Compliance","Risk","Bid Strategy"]:st.write("✓ "+x)
                r=run_all(st.session_state.company,t,txt);st.session_state.result=r;save_analysis(t["id"],st.session_state.company.get("company_name"),r);status.update(label="Analysis complete",state="complete")
            a,b,c=st.columns(3);a.metric("Readiness",f"{r['eligibility']['readiness']}%");b.metric("Fit",f"{r['eligibility']['fit']}%");c.metric("Risk",r["risk"]["risk_level"])
    if st.button("Next → Compliance & Report",type="primary",use_container_width=True):go("📋 Compliance & Reports")

elif page=="📋 Compliance & Reports":
    st.subheader("Compliance & Final Bid Intelligence")
    if "result" not in st.session_state:st.info("Run Agentic Analysis first.")
    else:
        r=st.session_state.result;t=st.session_state.selected_tender
        st.dataframe(pd.DataFrame(r["compliance"]["matrix"]),hide_index=True,use_container_width=True)
        docx=build_docx(st.session_state.company,t,r);pdf=build_pdf(st.session_state.company,t,r)
        a,b=st.columns(2);a.download_button("⬇ DOCX Report",docx,file_name=f"{t['id']}_TenderPulse.docx",use_container_width=True);b.download_button("⬇ PDF Report",pdf,file_name=f"{t['id']}_TenderPulse.pdf",mime="application/pdf",use_container_width=True)
        recipient=st.text_input("Company email",st.session_state.company.get("email",""))
        if st.button("Send Tender Alert Email"):
            ok,msg=send_alert(recipient,f"TenderPulse AI | {t['id']}",f"{t['title']}\nCategory: {t.get('category')}\nProcedure: {t.get('procedure')}\nDeadline: {t.get('deadline')}\nFit: {t.get('match',{}).get('fit')}%\nOfficial: {t.get('source_url')}")
            save_alert(t["id"],recipient,"sent" if ok else "failed");st.success(msg) if ok else st.error(msg)

elif page=="🗄 Database Inspector":
    st.subheader("Supabase Inspector")
    st.json(health());cols=st.columns(5)
    for c,t in zip(cols,["companies","tenders","matches","analyses","alerts"]):c.metric(t.title(),count(t))
    table=st.selectbox("Table",["companies","tenders","matches","analyses","alerts"]);rows=recent(table,10)
    if rows:st.dataframe(pd.DataFrame(rows),use_container_width=True)
    else:st.warning("No records found.")
