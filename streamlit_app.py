import json
from datetime import date,timedelta
import pandas as pd
import plotly.express as px
import streamlit as st
from src.config import DATA_DIR
from src.ui.components import hero,inject_v3_css,progress_header
from src.ui.cards import tender_card
from src.services.live_discovery import discover,source_registry
from src.connectors.registry import fetch_all
from src.services.official_search import search_official
from src.services.matcher import top_matches
from src.services.document_service import extract_text
from src.services.email_service import send_alert
from src.agents.pipeline import run_all
from src.agents.trace_pipeline import run_with_trace
from src.services.tender_document import fetch_document
from src.db.supabase_store import health,save_company,save_tender,save_match,save_analysis,save_alert,count,recent,list_tenders,saved_companies,save_or_update_company,company_matches,selectable_companies
from src.reporting.report_builder import build_docx,build_pdf
from src.simulation import national_simulation,yearly_company_demo
from src.services.profile_analytics import completeness,yearly_progress,seven_day_real

st.set_page_config(page_title="TenderPulse AI",page_icon="⚡",layout="wide")
inject_v3_css();hero()
PAGES=["🏠 Command Center","🏢 Company Profile","📡 Tender Radar","🧠 Agentic Analysis","📋 Compliance & Reports","🗄 Database Inspector"]
def load(n):return json.loads((DATA_DIR/n).read_text())
_sample_companies=load("sample_companies.json")
_saved=saved_companies() if health().get("ok") else []
if "company" not in st.session_state:
    st.session_state.company=(_saved[0] if _saved else _sample_companies[0])
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
    st.markdown("#### Active Company")
    _available_companies=selectable_companies() if health().get("ok") else []
    if not _available_companies:
        _available_companies=_sample_companies
    _names=[x.get("company_name","Unnamed company") for x in _available_companies]
    _current=st.session_state.company.get("company_name","")
    _idx=_names.index(_current) if _current in _names else 0
    _chosen=st.selectbox("Previously saved companies",_names,index=_idx,key="active_company_selector")
    _profile=next((x for x in _available_companies if x.get("company_name")==_chosen),_available_companies[0])
    if _profile.get("company_name") != st.session_state.company.get("company_name"):
        st.session_state.company=_profile
        st.session_state.matches=[]
        st.session_state.selected_tender=None
        st.session_state.pop("result",None)
        st.session_state.pop("agent_trace",None)
        st.rerun()
    st.session_state.active_company=st.session_state.company
    st.caption(f"Watching: {st.session_state.company.get('pec_category','—')} • {st.session_state.company.get('province','—')}")
    with st.expander("System Status"):
        st.write("Groq:", "🟢 configured" if __import__("src.services.groq_service",fromlist=["available"]).available() else "🟠 not configured")
        _db=health()
        st.write("Supabase:", "🟢 connected" if _db.get("ok") else "🔴 "+str(_db.get("status")))
        st.caption("TenderPulse V9 Corrected")

company=st.session_state.company
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
    _progress_cols=[c for c in ["Capability Index","Turnover PKR m","Projects"] if c in yp.columns]
    if _progress_cols:
        p2.plotly_chart(
            px.line(
                yp,
                x="Year",
                y=_progress_cols,
                markers=True,
                title=f"5-Year Company Progress — {company.get('company_name','Selected Company')}",
            ),
            use_container_width=True,
        )
    else:
        p2.info("Company progress data is not available yet.")
    st.markdown("### Last 7 Days — Matching Tender Trend")
    _history=company_matches(company.get("company_name"),500)
    sd=seven_day_real(_history)
    st.plotly_chart(px.bar(sd,x="Date",y="Matches",color="Category",barmode="group",title=f"Stored matches — {company.get('company_name')}"),use_container_width=True)
    if not _history:st.caption("No stored match history yet for this company. Run Tender Radar/cloud sync; this chart does not invent historical matches.")
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
            r=save_or_update_company(st.session_state.company);st.success("Saved to Supabase." if r.get("ok") else "Saved in session; inspect Supabase connection.")
    if st.button("Add C3 / C4 / C5 sample profiles to saved companies",use_container_width=True):
        _results=[save_or_update_company(x) for x in _sample_companies]
        if all(x.get("ok") for x in _results):st.success("Three SAMPLE profiles saved to Supabase. They remain clearly labelled SAMPLE.")
        else:st.warning("Some sample profiles could not be saved. Check Database Inspector.")
    st.markdown("### Profile Progress")
    _pc=completeness(st.session_state.company)
    st.progress(_pc/100,text=f"{_pc}% company profile complete")
    st.caption("A richer verified profile improves tender filtering: PEC codes, certificates, sectors, experience and turnover all matter.")
    st.link_button("Verify on official PEC","https://verification.pec.org.pk/")
    if st.button("Next → Search Matching Tenders",type="primary",use_container_width=True):go("📡 Tender Radar")

elif page=="📡 Tender Radar":
    st.subheader("Pakistan Public Tender Radar")
    st.caption("LIVE PUBLIC = parsed from official public source. Cached records come from the scheduled cloud sync. No synthetic provincial tender is presented as live.")
    with st.expander("Connector health / last cloud sync"):
        sync_rows=recent("source_sync_runs",20)
        if sync_rows: st.dataframe(pd.DataFrame(sync_rows),use_container_width=True,hide_index=True)
        else: st.info("No scheduled sync history yet. Run the GitHub Actions TenderPulse Public Tender Sync workflow once.")
    regions=st.multiselect("Search jurisdictions",["Federal","Punjab","Sindh","Khyber Pakhtunkhwa","Balochistan","AJK","Gilgit-Baltistan"],default=["Federal"])
    categories=st.multiselect("Procurement category",["Works","Goods","Non-Consultancy Services","Consultancy Services","Other"],default=["Works","Goods","Non-Consultancy Services","Consultancy Services"])
    procedures=st.multiselect("Procurement procedure",["SS1E","SS2E","Other/Unspecified"],default=["SS1E","SS2E","Other/Unspecified"],help="SS1E = Single Stage–One Envelope; SS2E = Single Stage–Two Envelope.")
    a,b,c=st.columns(3);minfit=a.slider("Minimum company fit",0,100,30,5);pages=b.slider("Maximum source pages",1,10,3);topn=c.selectbox("Results",[10,20,30,50])
    registry=source_registry()
    with st.expander("Official procurement sources"):
        for r in regions:st.link_button(f"Open {r} official source ↗",registry[r])
    if st.button("🔎 Search Open Sources & Match Company",type="primary"):
        with st.spinner("Reading selected public procurement sources…"):
            found,source_health=fetch_all(regions," ".join(st.session_state.company.get("keywords",[])[:6]))
            # Authenticity-first fallback: if a direct parser returns zero, search the public web index
            # but accept ONLY URLs on that region's official procurement domains.
            for _region in regions:
                _h=source_health.get(_region,{})
                if _h.get("records",0)==0:
                    _fallback=search_official(_region," ".join(company.get("keywords",[])[:6]),30)
                    if _fallback:
                        found.extend(_fallback)
                        source_health[_region]={"ok":True,"records":len(_fallback),"mode":"official-domain-search-fallback"}
        st.session_state.source_health=source_health
        st.caption("Fallback results are labelled OFFICIAL-DOMAIN DISCOVERY and are never presented as parser-verified open tenders. Open the official source before bidding.")
        for _r,_h in source_health.items():
            if not _h.get("ok"): st.warning(f"{_r}: connector error — {_h.get('error','unknown')}")
            elif _h.get("records",0)==0: st.info(f"{_r}: public source responded, but no normalized tender records were found in this run.")
        # If the scheduled cloud worker has already populated Supabase, merge cached live records.
        cached=[]
        for row in list_tenders(500):
            t=row.get("payload") or row
            if t.get("province") in regions or (t.get("scope")=="Federal" and "Federal" in regions):cached.append(t)
        byfp={}
        for t in found+cached:byfp[t.get("fingerprint") or t.get("id")]=t
        found=list(byfp.values())
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
        tender_card(t)
        st.markdown("### Tender document evidence")
        _doc_key=f"auto_doc_{t.get('id')}"
        if _doc_key not in st.session_state:st.session_state[_doc_key]=None
        _c1,_c2=st.columns(2)
        with _c1:
            if st.button("⚡ Fetch official tender document",use_container_width=True):
                with st.spinner("Finding and temporarily loading the official tender document…"):
                    st.session_state[_doc_key]=fetch_document(t)
        with _c2:
            up=st.file_uploader("Or upload PDF/DOCX/TXT",type=["pdf","docx","txt"],label_visibility="collapsed")
        _auto=st.session_state.get(_doc_key)
        if _auto:
            if _auto.get("ok"):
                st.success(f"Official document loaded temporarily: {_auto.get('name')} • {len(_auto.get('text','')):,} characters")
                st.link_button("Open fetched official document ↗",_auto["url"],use_container_width=True)
            else:
                st.warning(_auto.get("error","Official document could not be fetched automatically."))
                if _auto.get("url"):st.link_button("Open discovered document ↗",_auto["url"])
        if st.button("▶ Run Analysis Agents",type="primary"):
            txt=extract_text(up) if up else ((_auto or {}).get("text",""))
            _doc_url=(_auto or {}).get("url") or t.get("source_url","")
            with st.status("Executing agents…",expanded=True) as status:
                for x in ["Discovery","Company Digital Twin","PEC Verification","Document Intelligence","Eligibility","Compliance","Risk","Bid Strategy","Final Report"]:st.write("✓ "+x)
                r,agent_trace=run_with_trace(st.session_state.company,t,txt)
                r["source_evidence"]={"tender_id":t.get("id"),"official_tender_url":t.get("source_url"),"official_document_url":_doc_url,
                                      "document_auto_fetched":bool((_auto or {}).get("ok"))}
                st.session_state.result=r
                st.session_state.agent_trace=agent_trace
                save_analysis(t["id"],st.session_state.company.get("company_name"),r)
                status.update(label="Analysis complete",state="complete")
            st.markdown("### Live Agent Activity")
            st.caption("Evidence workflow • each card shows the agent task and concise result/hand-off.")
            _trace=st.session_state.agent_trace
            for _i in range(0,len(_trace),3):
                _cols=st.columns(3)
                for _j,_step in enumerate(_trace[_i:_i+3]):
                    with _cols[_j]:
                        st.markdown(f"""<div style="min-height:190px;border:1px solid #24485a;border-radius:14px;padding:16px;background:#0d1b2a">
                        <div style="color:#36e0b2;font-weight:800">✓ {_step['agent']}</div>
                        <div style="font-size:12px;color:#8fa6b7;margin:6px 0 12px">{_step['time']} • COMPLETE</div>
                        <div style="font-size:12px;color:#b8c7d1"><b>TASK</b><br>{_step['task']}</div>
                        <div style="font-size:13px;color:#ffffff;margin-top:12px"><b>RESULT</b><br>{_step['output']}</div>
                        </div>""",unsafe_allow_html=True)
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
