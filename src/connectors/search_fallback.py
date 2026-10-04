import hashlib, re, xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from urllib.parse import quote,urlparse,parse_qs,unquote
from .source_catalog import OFFICIAL_SOURCES
from .common import finalize
from .http_utils import get

def _allowed(u,region):
    host=(urlparse(u).hostname or "").lower()
    return any(host==d or host.endswith("."+d) for d in OFFICIAL_SOURCES[region]["domains"])
def _ddg_clean(h):
    if "duckduckgo.com/l/?" in h:
        try:return unquote(parse_qs(urlparse(h).query).get("uddg",[""])[0])
        except:return ""
    return h
def _record(region,u,title,desc,engine):
    t=finalize({"id":"DISC-"+hashlib.sha1(u.encode()).hexdigest()[:12].upper(),"title":title[:320] or "Official procurement result",
      "description":desc[:1800],"agency":region+" public procurement","advertised":"","deadline":"",
      "scope":"Federal" if region=="Federal" else "Provincial","province":region,
      "source":region+" official procurement","source_url":u})
    t["evidence_status"]="OFFICIAL-DOMAIN DISCOVERY"
    t["discovery_engine"]=engine
    t["verification_note"]="Official-domain discovery. Open the source to confirm active status, closing date, corrigenda and requirements."
    return t
def discover(region,keywords="",limit=50):
    """Two-engine public-index fallback. Results survive only when URL host is on the official allowlist."""
    if region not in OFFICIAL_SOURCES:return []
    domains=OFFICIAL_SOURCES[region]["domains"]
    queries=[]
    for domain in domains:
        queries.extend([f"site:{domain} tender procurement bid 2026 {keywords}",f'site:{domain} "closing date" 2026 {keywords}'])
    out=[];seen=set()
    for q in queries:
        # Bing RSS is machine-readable and often works where a portal itself times out.
        try:
            r=get("https://www.bing.com/search",params={"q":q,"format":"rss","count":"50"},timeout=15)
            if r.ok:
                root=ET.fromstring(r.text)
                for item in root.findall(".//item"):
                    u=(item.findtext("link") or "").strip(); title=item.findtext("title") or ""; desc=item.findtext("description") or ""
                    if u and u not in seen and _allowed(u,region):
                        seen.add(u);out.append(_record(region,u,title,desc,"Bing RSS"))
                        if len(out)>=limit:return out
        except Exception:pass
        # DuckDuckGo HTML second source.
        try:
            r=get("https://html.duckduckgo.com/html/?q="+quote(q),timeout=15)
            if r.ok:
                soup=BeautifulSoup(r.text,"html.parser")
                for res in soup.select(".result"):
                    a=res.select_one(".result__a")
                    if not a:continue
                    u=_ddg_clean(a.get("href","")); sn=res.select_one(".result__snippet")
                    if u and u not in seen and _allowed(u,region):
                        seen.add(u);out.append(_record(region,u," ".join(a.stripped_strings)," ".join(sn.stripped_strings) if sn else "","DuckDuckGo"))
                        if len(out)>=limit:return out
        except Exception:pass
    return out
