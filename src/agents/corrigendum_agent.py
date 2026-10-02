import hashlib,json
def fingerprint(tender):
    keys=["title","deadline","security_m","required_codes","min_category","min_turnover_m","min_experience"]
    return hashlib.sha256(json.dumps({k:tender.get(k) for k in keys},sort_keys=True).encode()).hexdigest()[:16]
def compare(old,new):
    changes={k:{"before":old.get(k),"after":new.get(k)} for k in set(old)|set(new) if old.get(k)!=new.get(k)}
    return {"status":"changed" if changes else "unchanged","changes":changes,"fingerprint":fingerprint(new)}
