import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .common import get,text,finalize
URL="https://epms.ppra.gov.pk/public/tenders/active-tenders"
def fetch(pages=5):
    out=[];seen=set()
    for page in range(1,pages+1):
        try:
            r=get(URL,{"page":page});s=BeautifulSoup(r.text,"html.parser")
            for a in s.find_all("a",href=True):
                m=re.search(r"/tender-details/(TS\d+E)",a["href"])
                if not m or m.group(1) in seen:continue
                tid=m.group(1);seen.add(tid);row=a.find_parent(["tr","div","li"]);blob=text(row) or text(a)
                dates=re.findall(r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+20\d{2}(?:\s+\d{1,2}:\d{2}\s+[AP]M)?",blob)
                out.append(finalize({"id":tid,"title":text(a)[:280] or blob[:280],"description":blob[:1500],
                  "agency":"Federal PPRA / EPADS","advertised":dates[0] if dates else "",
                  "deadline":dates[-1] if dates else "","scope":"Federal","province":"Federal",
                  "source":"Federal PPRA / EPADS","source_url":urljoin(r.url,a["href"])}))
        except Exception:continue
    return out
