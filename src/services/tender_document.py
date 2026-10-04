import io, re, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlparse
from src.connectors.http_utils import get
MAX_BYTES=12*1024*1024
def _is_pdf(u):return ".pdf" in u.lower().split("?")[0]
def discover_document_url(tender):
    """Resolve a tender page to its most likely official PDF/DOCX/TXT attachment."""
    source=tender.get("source_url","")
    if not source:return None
    if any(source.lower().split("?")[0].endswith(x) for x in (".pdf",".doc",".docx",".txt")):return source
    try:
        r=get(source,timeout=18)
        if not r.ok:return None
        soup=BeautifulSoup(r.text,"html.parser")
        candidates=[]
        for a in soup.find_all("a",href=True):
            u=urljoin(source,a["href"]); label=(a.get_text(" ",strip=True)+" "+u).lower()
            score=0
            if ".pdf" in label:score+=8
            if any(k in label for k in ("tender notice","bidding document","download","tender document","advertisement")):score+=5
            if any(x in label for x in (".docx",".doc",".txt")):score+=3
            if score:candidates.append((score,u))
        return sorted(candidates,reverse=True)[0][1] if candidates else None
    except:return None
def fetch_document(tender):
    u=discover_document_url(tender)
    if not u:return {"ok":False,"url":None,"text":"","name":None,"error":"No downloadable tender document found on the official source page."}
    try:
        r=get(u,timeout=25)
        if not r.ok:return {"ok":False,"url":u,"text":"","name":None,"error":f"Document HTTP {r.status_code}"}
        data=r.content[:MAX_BYTES]; ct=(r.headers.get("content-type") or "").lower()
        name=urlparse(u).path.split("/")[-1] or "tender_document"
        text=""
        if "pdf" in ct or name.lower().endswith(".pdf"):
            from pypdf import PdfReader
            reader=PdfReader(io.BytesIO(data))
            text="\n".join((p.extract_text() or "") for p in reader.pages[:80])
        elif name.lower().endswith(".docx") or "wordprocessingml" in ct:
            from docx import Document
            d=Document(io.BytesIO(data));text="\n".join(p.text for p in d.paragraphs)
        elif name.lower().endswith(".txt") or "text/plain" in ct:
            text=data.decode("utf-8","ignore")
        else:
            # Some official sites serve PDFs as octet-stream.
            if data[:4]==b"%PDF":
                from pypdf import PdfReader
                reader=PdfReader(io.BytesIO(data));text="\n".join((p.extract_text() or "") for p in reader.pages[:80])
        if not text.strip() and ("text/html" in ct or data[:32].lstrip().lower().startswith(b"<")):
            try:
                soup=BeautifulSoup(data.decode("utf-8","ignore"),"html.parser")
                text="\n".join(x.strip() for x in soup.stripped_strings if x.strip())
            except Exception:
                pass
        return {"ok":bool(text.strip()),"url":u,"text":text[:180000],"name":name,"bytes":data,
                "error":None if text.strip() else "The official file was reached, but it has no machine-extractable text (for example, a scanned/image PDF). Upload a text-searchable copy for document-grounded analysis."}
    except Exception as e:return {"ok":False,"url":u,"text":"","name":None,"error":str(e)}
