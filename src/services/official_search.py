import re, requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urlparse, parse_qs, unquote
from datetime import date, datetime
from src.connectors.common import finalize, category, procedure

OFFICIAL_DOMAINS={
 "Punjab":["ppra.punjab.gov.pk","epms.ppra.gov.pk"],
 "Sindh":["e.pprasindh.gov.pk","ppms.pprasindh.gov.pk","pprasindh.gov.pk"],
 "Khyber Pakhtunkhwa":["kppra.gov.pk","www.kppra.gov.pk"],
 "Balochistan":["bppra.gob.pk","www.bppra.gob.pk"],
 "Federal":["epms.ppra.gov.pk","ppra.gov.pk"],
 "AJK":["ajkppra.gov.pk","www.ajkppra.gov.pk"],
 "Gilgit-Baltistan":["gbppra.gov.pk","www.gbppra.gov.pk"],
}
UA={"User-Agent":"Mozilla/5.0 (compatible; TenderPulseAI/7.0; authenticity-first procurement discovery)"}

def _clean_ddg(href):
    if not href:return ""
    if "duckduckgo.com/l/?" in href:
        try:return unquote(parse_qs(urlparse(href).query).get("uddg",[""])[0])
        except:return ""
    return href

def _allowed(url,region):
    host=urlparse(url).netloc.lower().split(":")[0]
    return any(host==d or host.endswith("."+d) for d in OFFICIAL_DOMAINS.get(region,[]))

def _dates(text):
    pats=[
      r"\b\d{1,2}[-/]\d{1,2}[-/](?:20)?\d{2}\b",
      r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+20\d{2}\b",
      r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*,?\s+20\d{2}\b"
    ]
    out=[]
    for p in pats:out+=re.findall(p,text,re.I)
    return out[:6]

def search_official(region,keywords="",limit=30):
    """Fallback discovery through public web index, but accepts ONLY official-domain URLs.
    Search results are evidence leads, not automatically treated as verified-open tenders."""
    domains=OFFICIAL_DOMAINS.get(region,[])
    if not domains:return []
    q=f'site:{domains[0]} tender procurement bid 2026 {keywords}'.strip()
    url="https://html.duckduckgo.com/html/?q="+quote(q)
    try:
        r=requests.get(url,headers=UA,timeout=20);r.raise_for_status()
    except Exception:return []
    soup=BeautifulSoup(r.text,"html.parser");rows=[];seen=set()
    for result in soup.select(".result"):
        a=result.select_one(".result__a")
        if not a:continue
        href=_clean_ddg(a.get("href",""))
        if not href or href in seen or not _allowed(href,region):continue
        seen.add(href)
        title=" ".join(a.stripped_strings)
        sn=result.select_one(".result__snippet");snippet=" ".join(sn.stripped_strings) if sn else ""
        blob=(title+" "+snippet).strip()
        ds=_dates(blob)
        t=finalize({"id":f"SEARCH-{region[:3].upper()}-{len(rows)+1:04d}","title":title[:280],
          "description":snippet[:1600],"agency":f"{region} official-domain discovery",
          "advertised":ds[0] if ds else "","deadline":ds[-1] if len(ds)>1 else "",
          "scope":"Federal" if region=="Federal" else "Provincial","province":region,
          "source":f"{region} official-domain web discovery","source_url":href})
        t["evidence_status"]="OFFICIAL-DOMAIN DISCOVERY"
        t["verification_note"]="URL is restricted to an official procurement domain. Open the source to confirm current tender status and full requirements."
        rows.append(t)
        if len(rows)>=limit:break
    return rows
