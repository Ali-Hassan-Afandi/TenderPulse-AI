import requests,re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .common import finalize
URL="https://www.ajkppra.gov.pk/"
def fetch():
    try:
        s=BeautifulSoup(requests.get(URL,headers={"User-Agent":"Mozilla/5.0"},timeout=25).text,"html.parser");out=[]
        for tr in s.select("tr"):
            td=tr.find_all("td"); vals=[" ".join(x.stripped_strings) for x in td]
            if len(vals)<5:continue
            blob=" | ".join(vals); dates=re.findall(r"\b\d{1,2}[-/]\d{1,2}[-/]20\d{2}\b",blob)
            if len(dates)<2:continue
            links=tr.find_all("a",href=True); href=urljoin(URL,links[-1]["href"]) if links else URL
            title=next((v for v in vals if len(v)>18 and not re.match(r"^\d",v)),"AJK procurement")
            out.append(finalize({"id":"AJK-"+str(len(out)+1),"title":title[:300],"description":blob[:1600],
             "agency":vals[-2] if len(vals)>1 else "AJK agency","advertised":dates[0],"deadline":dates[1],
             "scope":"Provincial","province":"AJK","source":"AJ&K PPRA","source_url":href}))
        return out[:150]
    except:return []
