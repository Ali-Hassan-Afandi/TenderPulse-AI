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
