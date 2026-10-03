import html,streamlit as st
def tender_card(t):
    m=t.get("match",{});score=m.get("fit",0)
    st.markdown(f"""<div class="tp-card"><div class="tp-row"><span class="tp-badge">{html.escape(t.get('scope',''))}</span><span class="tp-fit">{score}% FIT</span></div>
    <h3>{html.escape(t.get('title','Untitled')[:150])}</h3><p>{html.escape(t.get('agency',''))}</p>
    <div class="tp-meta">📅 {html.escape(str(t.get('deadline','Unknown')))} &nbsp; • &nbsp; 🧾 {html.escape(t.get('id',''))}</div>
    <div class="tp-reason">{html.escape(m.get('reason',''))}</div></div>""",unsafe_allow_html=True)
