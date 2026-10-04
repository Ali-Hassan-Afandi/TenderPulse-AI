import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .common import finalize
from .http_utils import get
from .search_fallback import discover

URL="https://eproc.punjab.gov.pk/ActiveTenders.aspx"

def _parse(html):
    soup=BeautifulSoup(html,"html.parser"); out=[]; seen=set()
    for tr in soup.select("table tr"):
        td=tr.find_all("td")
        if len(td)<3: continue
        vals=[" ".join(x.stripped_strings) for x in td]
        blob=" | ".join(vals).strip()
        if len(blob)<20: continue
        links=tr.find_all("a",href=True)
        href=urljoin(URL,links[-1]["href"]) if links else URL
        key=href+"|"+blob[:160]
        if key in seen: continue
        seen.add(key)
        dates=re.findall(r"\b(?:\d{1,2}[-/]\d{1,2}[-/](?:20)?\d{2}|20\d{2}-\d{1,2}-\d{1,2})\b",blob)
        title=next((v for v in vals if len(v)>12 and not re.fullmatch(r"[\d\s./:-]+",v)), vals[0])
        ref=re.search(r"\b(?:TS|TSE|EP|PPRA)[-/\w]*\d+[-/\w]*\b",blob,re.I)
        out.append(finalize({"id":ref.group(0) if ref else f"PUN-{len(out)+1}",
          "title":title[:320],"description":blob[:1800],"agency":"Punjab e-Procurement",
          "advertised":dates[0] if dates else "","deadline":dates[-1] if len(dates)>1 else "",
          "scope":"Provincial","province":"Punjab","source":"Punjab e-Procurement","source_url":href}))
    return out

def fetch():
    try:
        r=get(URL,timeout=25); r.raise_for_status()
        rows=_parse(r.text)
        if rows:
            for x in rows:
                x["connector_mode"]="direct-active-tenders"
                x["evidence_status"]="LIVE PUBLIC"
                x["verification_note"]="Parsed from Punjab e-Procurement Active Tenders."
            return rows[:250]
    except Exception:
        pass
    rows=discover("Punjab","active tender eproc",60)
    for x in rows: x["connector_mode"]="official-index-fallback"
    return rows
