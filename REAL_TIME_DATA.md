# Real-Time Data Architecture
Current V4:
- Federal PPRA: live public HTML connector.
- AJ&K PPRA: live public HTML connector.
- GB PPRA: live public HTML connector.
- Punjab, Sindh, KP and Balochistan: official source links + clearly labelled simulation fallback until parsers are validated.

Production real-time design:
1. Scheduled ingestion worker runs every 30–60 minutes outside Streamlit.
2. Each jurisdiction has its own connector adapter.
3. Raw records are normalized to one Tender schema.
4. Tender ID + content fingerprint de-duplicates records.
5. Corrigendum changes create new versions.
6. Supabase stores tenders and company matches.
7. Streamlit reads Supabase instead of scraping on every page load.
8. Daily 08:00 PKT worker emails only new qualifying matches.

Do not call this "real-time" if a portal is only being simulated. Label each record LIVE PUBLIC, CACHED LIVE, or SIMULATION.
