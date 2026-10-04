from .search_fallback import discover
def fetch():
    rows=discover("Balochistan","",60)
    for x in rows:x["connector_mode"]="official-index"
    return rows
