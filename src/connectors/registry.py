from . import federal,punjab,sindh,kp,balochistan,ajk,gb
CONNECTORS={"Federal":federal.fetch,"Punjab":punjab.fetch,"Sindh":sindh.fetch,"Khyber Pakhtunkhwa":kp.fetch,
"Balochistan":balochistan.fetch,"AJK":ajk.fetch,"Gilgit-Baltistan":gb.fetch}
def fetch_all(regions=None):
    regions=regions or list(CONNECTORS);rows=[];health={}
    for region in regions:
        try:
            data=CONNECTORS[region]();rows+=data;health[region]={"ok":True,"records":len(data)}
        except Exception as e:health[region]={"ok":False,"records":0,"error":str(e)[:240]}
    return rows,health
