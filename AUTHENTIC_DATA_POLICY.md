# TenderPulse V7 Authentic Data Policy
1. Direct parser records are labelled LIVE PUBLIC.
2. If a provincial parser returns zero, TenderPulse may use official-domain search fallback.
3. Search fallback accepts only URLs whose host is in the hard-coded official procurement-domain allowlist.
4. Fallback records are labelled OFFICIAL-DOMAIN DISCOVERY, not "verified open".
5. TenderPulse never creates synthetic provincial tenders as live data.
6. A bidder should open the official source and confirm closing date, corrigenda, PEC requirements, procedure and documents.
7. Saved company profiles live in Supabase; Streamlit sleep does not erase them.
8. C3/C4/C5 bundled profiles are SAMPLE profiles, not claims about real registered firms.
