# Provincial connectors
Federal is already normalized. Punjab, Sindh, KP and Balochistan currently expose different public portal structures and therefore need separate tested adapters.

V5 behavior:
- Never invent provincial live tenders.
- Shows official portal/source navigation.
- Keeps unsupported connector output explicitly SIMULATION.
- Federal/AJK/GB supported parsers remain separate.

Next production step:
1. Inspect each public portal network/HTML.
2. Build one adapter per province.
3. Normalize to Tender schema.
4. Persist raw + normalized record in Supabase.
5. Add source_sync_runs table.
6. Run adapters on cloud schedule, not on every Streamlit render.
7. UI reads Supabase cache.
