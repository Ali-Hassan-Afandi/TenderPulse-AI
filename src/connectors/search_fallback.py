import requests,hashlib
from bs4 import BeautifulSoup
from urllib.parse import quote,urlparse,parse_qs,unquote
from .source_catalog import OFFICIAL_SOURCES
from .common import finalize
UA={"User-Agent":"Mozilla/5.0 (TenderPulseAI/8.0)"}
def _clean(h):
    if not h:return ""
    if "duckduckgo.com/l/?" in h:
        try:return unquote(parse_qs(urlparse(h).query).get("uddg",[""])[0])
        except:return ""
    return h
def _allowed(u,r):
    host=urlparse(u).netloc.lower().split(":")[0]
    return any(host==d or host.endswith("."+d) for d in OFFICIAL_SOURCES[r]["domains"])
def discover(region,keywords="",limit=40):
    if region not in OFFICIAL_SOURCES:return []
    domain=OFFICIAL_SOURCES[region]["domains"][0]; out=[];seen=set()
    for q in [f"site:{domain} tender procurement bid 2026 {keywords}",f'site:{domain} "closing date" tender 2026 {keywords}']:
        try:
            x=requests.get("https://html.duckduckgo.com/html/?q="+quote(q),headers=UA,timeout=18)
            soup=BeautifulSoup(x.text,"html.parser")
        except Exception:continue
        for res in soup.select(".result"):
            a=res.select_one(".result__a")
            if not a:continue
            u=_clean(a.get("href",""))
            if not u or u in seen or not _allowed(u,region):continue
            seen.add(u); sn=res.select_one(".result__snippet")
            title=" ".join(a.stripped_strings); desc=" ".join(sn.stripped_strings) if sn else ""
            t=finalize({"id":"SEARCH-"+hashlib.sha1(u.encode()).hexdigest()[:12].upper(),"title":title[:320],
              "description":desc[:1800],"agency":region+" procurement","advertised":"","deadline":"",
              "scope":"Federal" if region=="Federal" else "Provincial","province":region,"source":region+" official procurement","source_url":u})
            t["evidence_status"]="OFFICIAL-DOMAIN DISCOVERY"
            t["verification_note"]="Official-domain discovery. Open the official source and confirm current active status, closing date and requirements."
            out.append(t)
            if len(out)>=limit:return out
    return out
