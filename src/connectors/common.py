import hashlib,re,requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
UA={"User-Agent":"Mozilla/5.0 (compatible; TenderPulseAI/6.0; public-procurement-monitor)"}
def get(url,params=None,timeout=25):
    r=requests.get(url,params=params,headers=UA,timeout=timeout);r.raise_for_status();return r
def text(el): return " ".join(el.stripped_strings) if el else ""
def category(s):
    x=s.lower()
    if "non-consult" in x:return "Non-Consultancy Services"
    if "consult" in x or "expression of interest" in x or "request for proposal" in x:return "Consultancy Services"
    if any(k in x for k in ["construction","civil work","rehabilitation","road","building","works"]):return "Works"
    if any(k in x for k in ["goods","supply","purchase","equipment","material"]):return "Goods"
    return "Other"
def procedure(s):
    x=s.lower().replace("–","-")
    if "single stage two envelope" in x or "single stage-two envelope" in x:return "SS2E"
    if "single stage one envelope" in x or "single stage-one envelope" in x or "single stage single envelope" in x:return "SS1E"
    return "Other/Unspecified"
def fingerprint(t):
    raw="|".join(str(t.get(k,"")) for k in ["id","title","deadline","agency","source_url"])
    return hashlib.sha256(raw.encode()).hexdigest()
def finalize(t):
    t["category"]=t.get("category") or category(t.get("description","")+" "+t.get("title",""))
    t["procedure"]=t.get("procedure") or procedure(t.get("description",""))
    t["fingerprint"]=fingerprint(t);t["status"]="LIVE PUBLIC";return t
def generic_links(url,province,source,patterns=("tender","bid","procurement"),limit=80):
    r=get(url);s=BeautifulSoup(r.text,"html.parser");out=[];seen=set()
    for a in s.find_all("a",href=True):
        label=text(a);href=urljoin(r.url,a["href"]);hay=(label+" "+href).lower()
        if len(label)<8 or not any(p in hay for p in patterns):continue
        key=href
        if key in seen:continue
        seen.add(key)
        out.append(finalize({"id":f"{province[:3].upper()}-{len(out)+1:04d}","title":label[:280],
          "description":label,"agency":source,"advertised":"","deadline":"","scope":"Provincial",
          "province":province,"source":source,"source_url":href}))
        if len(out)>=limit:break
    return out
