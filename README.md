# TenderPulse AI

**Agentic Procurement Intelligence for Pakistan**

TenderPulse AI is a hackathon-ready Streamlit application that demonstrates a national tender-intelligence workflow: public tender discovery, company capability profiling, PEC public-source verification support, Groq-powered tender analysis, deterministic eligibility/compliance scoring, bid-readiness intelligence, email alerts, Pakistan-wide simulated analytics, and guided next actions.

## Important distinction
Live public-source connectors are separated from **clearly labelled demo/simulation data**. The app never represents simulated tenders, revenue, awards, or bid probabilities as government facts. The "Opportunity Fit" and "Bid Readiness" scores measure evidence alignment; they do not predict who will receive a public contract.

## Stack
- Python 3.12 recommended
- Streamlit
- Groq API
- Requests + BeautifulSoup public-web adapters
- Pydantic validation
- Pandas + Plotly
- SMTP email
- PyPDF / python-docx document extraction

## Repository
```text
TenderPulse_AI/
├── streamlit_app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   ├── config.toml
│   └── secrets.example.toml
├── data/
│   ├── demo_company.json
│   └── demo_tenders.json
└── src/
    ├── config.py
    ├── models.py
    ├── scoring.py
    ├── simulation.py
    ├── ui/
    │   └── components.py
    └── services/
        ├── groq_service.py
        ├── tender_sources.py
        ├── pec_service.py
        ├── document_service.py
        └── email_service.py
```

## Local setup
1. `python -m venv .venv`
2. Windows: `.venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. Copy `.streamlit/secrets.example.toml` to `.streamlit/secrets.toml`
5. Add your Groq key.
6. `streamlit run streamlit_app.py`

## Streamlit Cloud
Push this repository to GitHub. In Streamlit Community Cloud choose the repository, branch `main`, and `streamlit_app.py`. Open **Advanced settings / Secrets** and paste the contents of your real `secrets.toml`. Never commit the real secrets file.

## Email
Email works only when SMTP secrets are configured. Gmail typically requires 2-Step Verification + an App Password. The recipient defaults to the company-profile email and remains user-controlled.

## PEC verification
The module opens/queries public PEC web surfaces and returns source links/status. Because a stable documented public PEC JSON API is not assumed, it does **not** bypass login, CAPTCHA, access controls, or fabricate a verification. For production, replace/extend the adapter only with an officially permitted PEC endpoint/data feed.

## Commercial hardening
Add PostgreSQL/Supabase, persistent object storage, authentication/RBAC, audit logs, background jobs, official/permissioned procurement feeds, OCR, malware scanning, observability, rate limiting, encrypted company-document vault, and legal/security review before production.
