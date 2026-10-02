import re, math
from collections import Counter

def chunks(text,size=1200,overlap=180):
    text=re.sub(r"\s+"," ",text or "").strip()
    if not text:return []
    out=[]; i=0
    while i<len(text):
        out.append(text[i:i+size]); i+=max(1,size-overlap)
    return out

def _tokens(s): return re.findall(r"[a-zA-Z0-9]+",(s or "").lower())

def retrieve(text,query,top_k=6):
    q=Counter(_tokens(query)); scored=[]
    for i,d in enumerate(chunks(text)):
        c=Counter(_tokens(d)); score=sum(min(c[t],n) for t,n in q.items())/max(1,math.sqrt(sum(c.values())))
        scored.append({"chunk_id":i,"score":round(score,4),"text":d})
    return sorted(scored,key=lambda x:x["score"],reverse=True)[:top_k]
