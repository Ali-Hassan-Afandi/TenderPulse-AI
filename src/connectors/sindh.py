import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .common import get,text,finalize
URL="https://e.pprasindh.gov.pk/tenderlst?tender_list%5Bpage%5D=2026&tender_list%5Bsort%5D%5Bclose_date%5D=ASC"
def fetch():
    r=get(URL);s=BeautifulSoup(r.text,"html.parser");out=[]
    for tr in s.find_all("tr"):
        td=tr.find_all("td")
        if len(td)<7:continue
        cells=[text(x) for x in td]
        blob=" | ".join(cells)
        # SPPRA IDs vary; use first meaningful ID-like cell, otherwise stable row number
        sid=next((x for x in cells[:3] if re.search(r"\d",x) and len(x)<80),f"SPPRA-{len(out)+1}")
        a=tr.find("a",href=True)
        out.append(finalize({"id":"SD-"+re.sub(r"[^A-Za-z0-9-]","",sid)[:60],"title":cells[2][:280] if len(cells)>2 else blob[:280],
          "description":blob[:1800],"agency":cells[2] if len(cells)>2 else "Sindh SPPRA",
          "advertised":cells[3] if len(cells)>3 else "","deadline":cells[4] if len(cells)>4 else "",
          "scope":"Provincial","province":"Sindh","source":"Sindh SPPRA",
          "source_url":urljoin(r.url,a["href"]) if a else r.url}))
    return out[:250]
