import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

PEC_PORTAL="https://coportal.pec.org.pk/"
PEC_NAME_CHECK="https://coportal.pec.org.pk/User/NameCheck"

def public_pec_check(company_name, license_no):
    # Conservative public-source verification helper. No bypassing authentication/CAPTCHA.
    result={"status":"MANUAL_CONFIRMATION_REQUIRED","company":company_name,"license":license_no,
            "source":PEC_PORTAL,"notes":[]}
    try:
        r=requests.get(PEC_PORTAL,timeout=10,headers={"User-Agent":"TenderPulseAI-Hackathon/1.0"})
        result["portal_reachable"]=r.ok
        result["notes"].append("PEC public constructor/operator portal is reachable." if r.ok else f"PEC returned HTTP {r.status_code}.")
    except Exception as e:
        result["portal_reachable"]=False
        result["notes"].append(f"PEC portal could not be reached: {e}")
    result["notes"].append("This build does not assume an undocumented PEC verification API. Confirm the firm/license on PEC's official public interface.")
    return result
