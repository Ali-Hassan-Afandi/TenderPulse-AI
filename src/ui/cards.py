import html,streamlit as st
def tender_card(t):
    m=t.get("match",{});score=m.get("fit",0);url=html.escape(t.get("source_url","#"),quote=True)
    st.markdown(f"""<a class="tp-card-link" href="{url}" target="_blank"><div class="tp-card">
    <div class="tp-row"><span class="tp-badge">{html.escape(t.get('category','Other'))} • {html.escape(t.get('procedure',''))}</span><span class="tp-fit">{score}% FIT</span></div>
    <h3>{html.escape(t.get('title','Untitled')[:170])}</h3><p>{html.escape(t.get('agency',''))}</p>
    <div class="tp-meta">📍 {html.escape(t.get('province') or t.get('scope',''))} &nbsp; 📅 {html.escape(str(t.get('deadline','Unknown')))} &nbsp; 🧾 {html.escape(t.get('id',''))}</div>
    <div class="tp-reason">{html.escape(m.get('reason',''))}</div><div class="tp-open">Open official tender ↗</div></div></a>""",unsafe_allow_html=True)
