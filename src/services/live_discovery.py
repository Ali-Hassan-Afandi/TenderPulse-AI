import re,requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

UA={"User-Agent":"Mozilla/5.0 TenderPulseAI/4.0"}
SOURCES={
"Federal":"https://epms.ppra.gov.pk/public/tenders/active-tenders",
"Punjab":"https://ppra.punjab.gov.pk/public_procurement",
"Sindh":"https://www.e.pprasindh.gov.pk/",
"Khyber Pakhtunkhwa":"https://kppra.gov.pk/",
"Balochistan":"https://bppra.gob.pk/",
"AJK":"https://www.ajkppra.gov.pk/",
"Gilgit-Baltistan":"https://gbppra.gov.pk/"}

def _category(text):
    x=text.lower()
    if "non-consult" in x:return "Non-Consultancy Services"
    if "consult" in x or "request for proposal" in x:return "Consultancy Services"
    if "work" in x or "construction" in x or "rehabilitation" in x:return "Works"
    if "goods" in x or "supply" in x or "purchase" in x:return "Goods"
    return "Other"

def _procedure(text):
    x=text.lower().replace("–","-")
    if "single stage-two envelope" in x or "single stage two envelope" in x:return "SS2E"
    if "single stage-one envelope" in x or "single stage one envelope" in x:return "SS1E"
    return "Other/Unspecified"

def federal_live(max_pages=3):
    out=[]
    for page in range(1,max_pages+1):
        try:
            r=requests.get(SOURCES["Federal"],params={"page":page},headers=UA,timeout=20)
            soup=BeautifulSoup(r.text,"html.parser")
            for a in soup.find_all("a",href=True):
                href=a.get("href","")
                m=re.search(r"/tender-details/(TS\d+E)",href)
                if not m:continue
                tid=m.group(1); container=a.find_parent(["tr","div","li"]) or a.parent
                text=" ".join(container.stripped_strings) if container else a.get_text(" ",strip=True)
                dates=re.findall(r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+2026(?:\s+\d{1,2}:\d{2}\s+[AP]M)?",text)
                title=a.get_text(" ",strip=True)
                if len(title)<8:title=text[:220]
                out.append({"id":tid,"title":title[:260],"description":text[:1200],"agency":"Federal PPRA / EPADS",
                    "status":"LIVE PUBLIC","advertised":dates[0] if dates else "","deadline":dates[-1] if dates else "",
                    "scope":"Federal","province":"","source":"Federal PPRA / EPADS",
                    "source_url":urljoin(r.url,href),"category":_category(text),"procedure":_procedure(text)})
        except Exception:continue
    seen={};[seen.setdefault(x["id"],x) for x in out]
    return list(seen.values())

def ajk_live():
    out=[]
    try:
        r=requests.get(SOURCES["AJK"],headers=UA,timeout=20);s=BeautifulSoup(r.text,"html.parser")
        for tr in s.find_all("tr"):
            cells=[" ".join(x.stripped_strings) for x in tr.find_all(["td","th"])]
            if len(cells)<5:continue
            text=" | ".join(cells)
            nums=re.findall(r"\b\d{4}\b",text)
            if not nums:continue
            a=tr.find("a",href=True);url=urljoin(r.url,a["href"]) if a else r.url
            title=cells[1] if len(cells)>1 else text[:180]
            out.append({"id":"AJK-"+nums[0],"title":title,"description":text,"agency":cells[-2] if len(cells)>2 else "AJK",
                "status":"LIVE PUBLIC","advertised":cells[2] if len(cells)>2 else "","deadline":cells[3] if len(cells)>3 else "",
                "scope":"Provincial","province":"AJK","source":"AJ&K PPRA","source_url":url,"category":_category(text),"procedure":_procedure(text)})
    except Exception:pass
    return out[:100]

def gb_live():
    out=[]
    try:
        r=requests.get(SOURCES["Gilgit-Baltistan"],headers=UA,timeout=20);s=BeautifulSoup(r.text,"html.parser")
        text=s.get_text("\n",strip=True)
        ids=re.findall(r"TSE-\d+",text)
        for tid in dict.fromkeys(ids):
            pos=text.find(tid);chunk=text[pos:pos+700];lines=[x.strip() for x in chunk.splitlines() if x.strip()]
            title=lines[1] if len(lines)>1 else tid
            a=s.find("a",string=re.compile(re.escape(tid)));url=urljoin(r.url,a.get("href")) if a and a.get("href") else r.url
            dates=re.findall(r"\d{1,2}\s+[A-Z][a-z]{2},\s+2026",chunk)
            out.append({"id":tid,"title":title,"description":chunk,"agency":"GB PPRA","status":"LIVE PUBLIC",
                "advertised":dates[0] if dates else "","deadline":dates[-1] if dates else "",
                "scope":"Provincial","province":"Gilgit-Baltistan","source":"GB PPRA","source_url":url,
                "category":_category(chunk),"procedure":_procedure(chunk)})
    except Exception:pass
    return out[:100]

def discover(regions,pages=3):
    allrows=[]
    for region in regions:
        if region=="Federal":allrows+=federal_live(pages)
        elif region=="AJK":allrows+=ajk_live()
        elif region=="Gilgit-Baltistan":allrows+=gb_live()
    return allrows

def source_registry():return SOURCES
