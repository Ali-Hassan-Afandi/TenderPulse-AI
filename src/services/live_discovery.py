import re, requests
from bs4 import BeautifulSoup
from datetime import datetime
FEDERAL="https://epms.ppra.gov.pk/public/tenders/active-tenders"
SOURCES={"Punjab":"https://ppra.punjab.gov.pk/","Sindh":"https://www.e.pprasindh.gov.pk/",
"Khyber Pakhtunkhwa":"https://kppra.gov.pk/","Balochistan":"https://bppra.gob.pk/"}
def federal_live(max_pages=3):
    out=[]
    for page in range(1,max_pages+1):
        try:
            r=requests.get(FEDERAL,params={"page":page},headers={"User-Agent":"Mozilla/5.0 TenderPulse/1.0"},timeout=20)
            soup=BeautifulSoup(r.text,"html.parser")
            text=soup.get_text(" ",strip=True)
            # Parse visible tender IDs and surrounding text; source HTML can change, so this is intentionally defensive.
            ids=list(dict.fromkeys(re.findall(r"TS\d+E",text)))
            for tid in ids:
                pos=text.find(tid); snippet=text[pos:pos+900]
                dates=re.findall(r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+2026(?:\s+\d{1,2}:\d{2}\s+[AP]M)?",snippet)
                out.append({"id":tid,"title":snippet[:260],"description":snippet,"agency":"Federal PPRA / EPADS",
                "status":"LIVE PUBLIC","advertised":dates[0] if dates else "","deadline":dates[-1] if dates else "",
                "scope":"Federal","province":"","source":"Federal PPRA / EPADS","source_url":r.url})
        except Exception:continue
    seen={};[seen.setdefault(x["id"],x) for x in out]
    return list(seen.values())
def source_registry():return {"Federal":FEDERAL,**SOURCES}
