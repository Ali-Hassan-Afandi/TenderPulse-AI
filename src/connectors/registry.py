from . import federal,punjab,sindh,kp,balochistan,ajk,gb
from .search_fallback import discover
CONNECTORS={"Federal":federal.fetch,"Punjab":punjab.fetch,"Sindh":sindh.fetch,"Khyber Pakhtunkhwa":kp.fetch,
"Balochistan":balochistan.fetch,"AJK":ajk.fetch,"Gilgit-Baltistan":gb.fetch}
def fetch_all(regions=None,keywords=""):
    regions=regions or list(CONNECTORS);rows=[];health={}
    for region in regions:
        direct=[];error=None
        try:direct=CONNECTORS[region]() or []
        except Exception as e:error=str(e)
        fallback=[]
        # Supplement every sparse non-federal source. Direct official-index connectors already carry discovery labels.
        if region!="Federal" and len(direct)<10:
            try:fallback=discover(region,keywords,50)
            except Exception as e:
                if not error:error=f"fallback: {e}"
        seen=set();merged=[]
        for x in direct+fallback:
            key=x.get("source_url") or x.get("fingerprint") or x.get("id")
            if not key or key in seen:continue
            seen.add(key);merged.append(x)
        rows.extend(merged)
        health[region]={"ok":bool(merged),"direct":len(direct),"fallback":len(fallback),
          "records":len(merged),"error":error if not merged else None,
          "mode":"direct+official-index" if fallback else ("official-index" if direct and direct[0].get("evidence_status")=="OFFICIAL-DOMAIN DISCOVERY" else "direct")}
    return rows,health
