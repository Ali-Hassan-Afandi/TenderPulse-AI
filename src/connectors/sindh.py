from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .common import finalize
from .http_utils import get
URL="https://e.pprasindh.gov.pk/tenderlst?tender_list%5Bsort%5D%5Bclose_date%5D=DESC"
def fetch():
    r=get(URL,timeout=25); r.raise_for_status(); soup=BeautifulSoup(r.text,"html.parser");out=[]
    for tr in soup.select("table tr"):
        td=tr.find_all("td")
        if len(td)<8:continue
        v=[" ".join(x.stripped_strings) for x in td]
        if not v[1].strip():continue
        links=tr.find_all("a",href=True)
        notice=next((urljoin(URL,a["href"]) for a in links if "tender" in (a.get("href","").lower()) or "download" in (a.get_text(" ",strip=True).lower())), URL)
        title=(v[2]+" — SPPRA "+v[1])[:300]
        out.append(finalize({"id":"SPPRA-"+v[1],"title":title,"description":" | ".join(v[:8])[:1800],"agency":v[2],
          "advertised":v[3],"deadline":v[4],"scope":"Provincial","province":"Sindh","source":"Sindh SPPRA","source_url":notice}))
    return out[:250]
