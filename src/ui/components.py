import streamlit as st

def hero():
    st.markdown('''<div style="padding:26px;border:1px solid #1d3a4c;border-radius:22px;background:linear-gradient(135deg,#0c1d31,#092a2c);margin-bottom:18px">
    <div style="font-size:13px;letter-spacing:2px;color:#31E6B3">PAKISTAN • AGENTIC PROCUREMENT INTELLIGENCE</div>
    <h1 style="margin:5px 0 4px">TenderPulse AI</h1>
    <p style="margin:0;color:#b9c7d5">Discover → Verify → Analyze → Match → Prepare → Alert</p></div>''',unsafe_allow_html=True)

def process(step):
    stages=["Company","Sources","Analyze","Compliance","Notify"]
    st.progress(step/len(stages))
    st.caption("  →  ".join(("● "+x if i<step else "○ "+x) for i,x in enumerate(stages,1)))

def next_action(title, detail):
    st.info(f"**AutoGuide — Next step:** {title}\n\n{detail}")

def inject_v3_css():
    import streamlit as st
    st.markdown("""<style>
    .block-container{padding-top:1.4rem;max-width:1450px}
    .tp-card{background:linear-gradient(145deg,rgba(20,28,39,.96),rgba(12,18,28,.96));border:1px solid rgba(88,255,174,.18);border-radius:18px;padding:18px;margin:10px 0;box-shadow:0 12px 32px rgba(0,0,0,.16)}
    .tp-card h3{margin:.55rem 0;color:#f5f7fa;font-size:1.08rem}.tp-row{display:flex;justify-content:space-between;align-items:center}
    .tp-badge{font-size:.76rem;padding:5px 9px;border-radius:20px;background:rgba(92,130,255,.14)}
    .tp-fit{font-weight:800;font-size:1.08rem;color:#65f6ae}.tp-meta,.tp-reason{font-size:.84rem;color:#aeb8c6;margin-top:8px}
    div[data-testid="stMetric"]{background:rgba(18,27,39,.72);border:1px solid rgba(255,255,255,.08);padding:12px;border-radius:16px}
     .tp-card-link{text-decoration:none!important;color:inherit!important}.tp-card{transition:.18s ease}.tp-card:hover{transform:translateY(-3px);border-color:rgba(101,246,174,.65);box-shadow:0 18px 40px rgba(0,0,0,.28)}.tp-open{margin-top:12px;color:#65f6ae;font-weight:700} </style>""",unsafe_allow_html=True)

def progress_header(step,total,label):
    import streamlit as st
    st.progress(step/total,text=f"Step {step} of {total} — {label}")
def next_button(label,key):
    import streamlit as st
    return st.button(f"Next → {label}",key=key,type="primary",use_container_width=True)
