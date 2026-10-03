from . import federal,punjab,sindh,kp,balochistan,ajk,gb
from .search_fallback import discover
CONNECTORS={"Federal":federal.fetch,"Punjab":punjab.fetch,"Sindh":sindh.fetch,"Khyber Pakhtunkhwa":kp.fetch,
"Balochistan":balochistan.fetch,"AJK":ajk.fetch,"Gilgit-Baltistan":gb.fetch}
def fetch_all(regions=None,keywords=""):
    regions=regions or list(CONNECTORS); rows=[];health={}
    for region in regions:
        try:direct=CONNECTORS[region]() or [];err=None
        except Exception as e:direct=[];err=str(e)
        fallback=[]
        if region!="Federal" and len(direct)<5:
            try:fallback=discover(region,keywords,40)
            except:pass
        seen=set();merged=[]
        for x in direct+fallback:
            k=x.get("source_url") or x.get("fingerprint") or x.get("id")
            if k in seen:continue
            seen.add(k);merged.append(x)
        rows+=merged
        health[region]={"ok":bool(merged),"direct":len(direct),"fallback":len(fallback),"records":len(merged),"error":err}
    return rows,health
