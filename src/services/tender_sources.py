import requests
from bs4 import BeautifulSoup

FEDERAL_PUBLIC="https://epms.ppra.gov.pk/public/tenders/active-tenders"
SOURCE_DIRECTORY={
 "Federal PPRA / EPADS":FEDERAL_PUBLIC,
 "Punjab PPRA":"https://ppra.punjab.gov.pk/",
 "Sindh PPRA":"https://www.e.pprasindh.gov.pk/",
 "KP PPRA":"https://kppra.gov.pk/",
 "Balochistan PPRA":"https://bppra.gob.pk/"
}

def source_health():
    rows=[]
    for name,url in SOURCE_DIRECTORY.items():
        try:
            r=requests.get(url,timeout=8,headers={"User-Agent":"TenderPulseAI-Hackathon/1.0"})
            rows.append({"Source":name,"Reachable":r.ok,"HTTP":r.status_code,"URL":url})
        except Exception:
            rows.append({"Source":name,"Reachable":False,"HTTP":"—","URL":url})
    return rows

def federal_public_preview(limit=12):
    # Best-effort HTML adapter. Portal markup can change; demo data remains separate.
    try:
        r=requests.get(FEDERAL_PUBLIC,timeout=12,headers={"User-Agent":"Mozilla/5.0 TenderPulseAI"})
        r.raise_for_status()
        soup=BeautifulSoup(r.text,"html.parser")
        text=" ".join(soup.stripped_strings)
        return {"ok":True,"source":FEDERAL_PUBLIC,"preview":text[:2500],"note":"Live public page text preview; not a normalized official API feed."}
    except Exception as e:
        return {"ok":False,"source":FEDERAL_PUBLIC,"preview":"","note":str(e)}
