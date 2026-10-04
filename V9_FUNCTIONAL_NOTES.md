# TenderPulse V9 Functional
## Procurement ingestion
- Federal: direct official parser.
- Sindh: direct SPPRA table parser; retries the known expired certificate only for the allow-listed official Sindh host.
- GB/AJK: direct official parsers.
- Punjab/KP/Balochistan: official-domain public-index discovery is used because their public portals may not expose stable machine-readable tender feeds or may time out from cloud hosting.
- Discovery records remain OFFICIAL-DOMAIN DISCOVERY. They are never silently promoted to parser-verified active tenders.
## Agent analysis
- Automatically discovers/downloads an official tender PDF/DOCX/TXT where the tender/detail page exposes one.
- Bytes/text are held only in Streamlit session memory for analysis; they are not permanently stored by this feature.
- Analysis stores official tender URL + document URL in source_evidence.
- Agent cards show task/status/result, not hidden chain-of-thought.
