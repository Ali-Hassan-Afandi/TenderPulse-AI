import requests,re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .common import finalize
URL="https://gbppra.gov.pk/"
def fetch():
    try:
        s=BeautifulSoup(requests.get(URL,headers={"User-Agent":"Mozilla/5.0"},timeout=25).text,"html.parser");out=[];seen=set()
        for tr in s.select("tr"):
            vals=[" ".join(x.stripped_strings) for x in tr.find_all("td")]; blob=" | ".join(vals)
            if not vals or not re.search(r"(TSE|tender|procurement|bid)",blob,re.I):continue
            links=tr.find_all("a",href=True); href=urljoin(URL,links[-1]["href"]) if links else URL
            if href in seen:continue
            seen.add(href); dates=re.findall(r"\b(?:\d{1,2}[-/]\d{1,2}[-/]20\d{2}|20\d{2}-\d{1,2}-\d{1,2})\b",blob)
            tse=re.search(r"\bTSE[-\w/]*",blob,re.I)
            out.append(finalize({"id":tse.group(0) if tse else "GB-"+str(len(out)+1),"title":(vals[1] if len(vals)>1 else vals[0])[:300],
             "description":blob[:1600],"agency":"GB procuring agency","advertised":dates[0] if dates else "",
             "deadline":dates[-1] if len(dates)>1 else "","scope":"Provincial","province":"Gilgit-Baltistan","source":"GB PPRA","source_url":href}))
        return out[:150]
    except:return []
